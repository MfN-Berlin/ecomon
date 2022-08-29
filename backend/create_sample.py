import argparse
from os import path
from dotenv import load_dotenv
from util.db import connect_to_db
from sql.query import get_prediction_random_sample
from uuid import uuid4
import ffmpeg
import zipfile
import os
import shutil


PREFIX = "BRITZ01"
SPECIES = "fringilla_coelebs"

to_list_of_strings = lambda x: [str(i) for i in x]


def write_csv_file_from_list(filepath, list_of_lists, sep=",", header=None):
    with open(filepath, "w") as f:
        if header is not None:
            f.write(sep.join(header) + "\n")
        for i in list_of_lists:
            f.write(sep.join(to_list_of_strings(i)) + "\n")


def extract_part_from_audio_file_by_start_and_end_time(
    filepath, output_filepath, start_time, end_time, padding=0
):
    stime = start_time - padding if start_time - padding > 0 else 0
    etime = end_time + padding
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
    # print(query)
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
    try:
        for i in result:
            filepath = i[0]
            filename = path.basename(filepath)
            [stem, ext] = path.splitext(filename)
            out_filename = "{}_{}_c{}{}".format(
                stem, pad_int_with_zeros(int(i[2] * 1000), 9), i[5], ext
            )

            extract_part_from_audio_file_by_start_and_end_time(
                i[0],
                path.join(directory, out_filename),
                i[2],
                i[3],
                padding=audio_padding,
            )
            tmp = list(i)
            tmp.insert(1, out_filename)
            csv_list.append(tmp)

        header = [
            "original_filepath",
            "filepath",
            "record_datetime",
            "start_time",
            "end_time",
            "duration",
            "channel",
            species,
        ]

        write_csv_file_from_list(
            path.join(directory, "{}_{}_{}.csv".format(prefix, species, threshold)),
            csv_list,
            header=header,
        )

        if result_filepath is not None:
            zip_folder(directory, result_filepath)
            return result_filepath
        else:
            zip_filename = "{}_{}_{}_{}.zip".format(
                directoryName, prefix, species, threshold
            )
            zip_folder(directory, zip_filename)
            return zip_filename
    except Exception as e:
        # remove directory if it exists
        if path.exists(directory):
            shutil.rmtree(directory)
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

