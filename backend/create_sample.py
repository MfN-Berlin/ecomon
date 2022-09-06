import argparse
from os import path
from dotenv import load_dotenv
from util.db import connect_to_db
from sql.query import (
    get_prediction_random_sample,
    update_job_failed,
    update_job_progress,
)
from uuid import uuid4
import ffmpeg
import zipfile
import os
import shutil
import xlsxwriter
import json

PREFIX = "BRITZ01"
SPECIES = "fringilla_coelebs"

to_list_of_strings = lambda x: [str(i) for i in x]


def write_csv_file_from_list(filepath, list_of_lists, sep=",", header=None):
    with open(filepath, "w") as f:
        if header is not None:
            f.write(sep.join(header) + "\n")
        for i in list_of_lists:
            f.write(sep.join(to_list_of_strings(i)) + "\n")


def write_execl_file(filepath, rows, header):
    # load olaf_id.json file into dictionary
    olaf_id_list = json.load(open("./assets/olaf8_id.json"))
    olaf_id_dict = {}
    for entry in olaf_id_list:
        olaf_id_dict[entry["latin_name"].lower().replace(" ", "_")] = entry["olaf8_id"]
    # print(olaf_id_dict["fringilla_coelebs"])
    # which is the filename that we want to create.
    workbook = xlsxwriter.Workbook(filepath)

    # The workbook object is then used to add new
    # worksheet via the add_worksheet() method.
    worksheet = workbook.add_worksheet()
    # Iterate over the data and write it out row by row.
    for index, value in enumerate(header):
        worksheet.write(0, index, value[0])
        worksheet.set_column(index, index, len(value[0]))
    for row_index, row in enumerate(rows):
        for col_index, header_val in enumerate(header):
            if header_val[1] is not None:
                if header_val[1] == "filename":
                    worksheet.write_url(
                        row_index + 1,
                        col_index,
                        "./{}".format(row[header_val[1]]),
                        string=row[header_val[1]],
                    )
                    continue
                if header_val[0] == "SpeciesCode":
                    worksheet.write(
                        row_index + 1,
                        col_index,
                        olaf_id_dict[row[header_val[1]].lower().replace(" ", "_")],
                    )
                    continue
                worksheet.write(row_index + 1, col_index, row[header_val[1]])

    workbook.close()


def first_letter_to_upper_case(string):
    return string[0].upper() + string[1:]


def extract_part_from_audio_file_by_start_and_end_time(
    filepath, output_filepath, start_time, end_time, padding=0
):
    stime = start_time - padding if start_time - padding > 0 else 0
    etime = end_time + padding
    print("Run extract on ", filepath)
    ffmpeg.input(filepath, ss=stime, to=etime, v="error").output(output_filepath).run()


def zip_folder(folder_path, output_filepath):
    zip_file = zipfile.ZipFile(output_filepath, "w")
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            zip_file.write(os.path.join(root, file), file)
    zip_file.close()
    shutil.rmtree(folder_path)


def pad_int_with_zeros(num, digits):
    return str(num).zfill(digits)


# transform milliseconds to hh:mm:ss format
def s_to_time(s):
    centseconds = round(((s + 0.2) % 1) * 100)
    seconds = s
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    result = "%02d%02d%02d%02d" % (hours, minutes, seconds, centseconds)

    return result


def create_sample(
    prefix: str = PREFIX,
    species: str = SPECIES,
    threshold=0.95,
    sample_size=10,
    audio_padding=5,
    start_datetime=None,
    end_datetime=None,
    result_filepath=None,
    BAI_TMP_DIRECTORY=None,
    job_id=None,
):
    load_dotenv()
    db_connection = connect_to_db()
    db_cursor = db_connection.cursor()

    query = get_prediction_random_sample(
        prefix,
        sample_size,
        species,
        threshold,
        audio_padding=audio_padding,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )
    print(query)
    db_cursor.execute(query)
    result = db_cursor.fetchall()

    # create folder for samples
    directoryName = uuid4().hex
    directory = ""
    if BAI_TMP_DIRECTORY is None:
        directory = path.join(os.getcwd(), "tmp", directoryName)
    else:
        directory = path.join(BAI_TMP_DIRECTORY, directoryName)
    os.makedirs(directory, exist_ok=True)
    # create csv of results

    # create wav file for each prediction
    csv_list = []
    progress = 0
    length = len(result)

    try:
        for index, row in enumerate(result):
            filepath = row[0]
            filename = path.basename(filepath)
            start = float(row[2]) - audio_padding
            end = float(row[3]) + audio_padding
            [stem, ext] = path.splitext(filename)

            out_filename = "{stem}_S{start}_E{end}{ext}".format(
                stem=stem, start=s_to_time(start), end=s_to_time(end), ext=ext
            )
            # check if file not exists
            if not path.exists(path.join(directory, out_filename)):
                extract_part_from_audio_file_by_start_and_end_time(
                    row[0],
                    path.join(directory, out_filename),
                    row[2],
                    row[3],
                    padding=audio_padding,
                )
            # filepath,
            # record_datetime,
            # start_time,
            # end_time,
            # duration,
            # channel,
            # {species}
            tmp = {
                "filename": out_filename,
                "record_datetime": row[1],
                "start_time": row[2] - audio_padding,
                "end_time": row[3] + audio_padding,
                "duration": row[4],
                "channel": row[5],
                "confidence": row[6],
                "audio_padding": audio_padding,
                "species": first_letter_to_upper_case(species).replace("_", " "),
            }
            csv_list.append(tmp)
            if progress < round(index / length * 100):
                # print("{}%".format(round(index / length * 100)))
                progress = round(index / length * 100)
                if job_id is not None:
                    db_cursor.execute(update_job_progress(job_id, progress))
                    db_cursor.connection.commit()

        header = [
            ("Channel", "channel"),
            ("Begin Time (s)", "start_time"),
            ("End Time (s)", "end_time"),
            ("Delta Time (s)", "audio_padding"),
            ("Snippet", "filename"),
            ("PredictionClass", "species"),
            ("SpeciesCode", "species"),
            ("Confidence (p) ", "confidence"),
            ("ManualValidation", None),
            ("VocalizationTypeCode", None),
            ("Note", None),
        ]

        write_execl_file(
            path.join(directory, "{}_{}_{}.xlsx".format(prefix, species, threshold)),
            csv_list,
            header,
        )

        if result_filepath is not None:
            zip_folder(directory, result_filepath)
            if job_id is not None:
                db_cursor.execute(update_job_progress(job_id, 100))
                db_cursor.connection.commit()
            return result_filepath
        else:
            zip_filename = "{}_{}_{}_{}.zip".format(
                directoryName, prefix, species, threshold
            )
            zip_folder(directory, zip_filename)

            if job_id is not None:
                db_cursor.execute(update_job_progress(job_id, 100))
                db_cursor.connection.commit()
            return zip_filename
    except Exception as e:
        # remove directory if it exists
        if path.exists(directory):
            shutil.rmtree(directory)
        if (job_id is not None) and (db_cursor is not None):
            # cut error message to fit in db field
            error_message = str(e)[:255]
            db_cursor.execute(update_job_failed(job_id, error_message))
            db_cursor.connection.commit()
        raise e


if __name__ == "__main__":
    # read commandline arguments is prefix and drop flag
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default=PREFIX)
    parser.add_argument("--species", default=SPECIES)
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument("--sample_size", type=int, default=10)
    parser.add_argument("--audio_padding", type=int, default=5)
    parser.add_argument("--start_datetime", type=str, default=None)
    parser.add_argument("--end_datetime", type=str, default=None)
    parser.add_argument("--result_filepath", type=str, default=None)
    parser.add_argument("--BAI_TMP_DIRECTORY", type=str, default=None)
    args = parser.parse_args()
    create_sample(
        prefix=args.prefix,
        species=args.species,
        threshold=args.threshold,
        sample_size=args.sample_size,
        audio_padding=args.audio_padding,
        start_datetime=args.start_datetime,
        end_datetime=args.end_datetime,
        result_filepath=args.result_filepath,
        BAI_TMP_DIRECTORY=args.BAI_TMP_DIRECTORY,
    )

