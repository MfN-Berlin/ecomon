import argparse
from os import path
from dotenv import load_dotenv
from util.db import connect_to_db
from sql.query import (
    get_prediction_random_sample,
    get_predictions,
    get_job_by_id,
    update_job_failed,
    update_job_progress,
    update_job_metadata,
)
from uuid import uuid4

import os
import shutil
from util.tools import (
    s_to_time,
    pad_int_with_zeros,
    first_letter_to_upper_case,
    zip_folder_and_delete,
)
from util.audio import extract_part_from_audio_file_by_start_and_end_time
import json
from util.excel import write_execl_file
from logging  import getLogger
logger = getLogger(__name__)
PREFIX = "BRITZ01"
SPECIES = "fringilla_coelebs"

to_list_of_strings = lambda x: [str(i) for i in x]


def write_csv_file_from_list(filepath, list_of_lists, sep=",", header=None):
    with open(filepath, "w") as f:
        if header is not None:
            f.write(sep.join(header) + "\n")
        for i in list_of_lists:
            f.write(sep.join(to_list_of_strings(i)) + "\n")


def create_sample(
    prefix: str = PREFIX,
    species: str = SPECIES,
    threshold_min=0.95,
    threshold_max=1,
    sample_size=10,
    audio_padding=5,
    start_datetime=None,
    end_datetime=None,
    result_filepath=None,
    TMP_DIRECTORY=None,
    job_id=None,
    random=True,
    high_pass_frequency=0,
):
    logger.debug("High pass frequency: ", high_pass_frequency)
    load_dotenv()
    db_connection = connect_to_db()
    db_cursor = db_connection.cursor()

    query = (
        get_prediction_random_sample(
            prefix,
            sample_size,
            species,
            threshold_min,
            threshold_max,
            audio_padding=audio_padding,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        if random
        else get_predictions(
            prefix,
            species,
            threshold_min,
            threshold_max,
            audio_padding=audio_padding,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
    )

    db_cursor.execute(query)
    result = db_cursor.fetchall()

    # create folder for samples
    directoryName = uuid4().hex
    directory = ""
    if TMP_DIRECTORY is None:
        directory = path.join(os.getcwd(), "tmp", directoryName)
    else:
        directory = path.join(TMP_DIRECTORY, directoryName)
    os.makedirs(directory, exist_ok=True)
    # create csv of results

    # create wav file for each prediction
    csv_list = []
    progress = 0
    length = len(result)
    if job_id is not None:
        db_cursor.execute(get_job_by_id(job_id))
        job = db_cursor.fetchone()
        metadata = job[4]
        metadata["samples"] = length
        db_cursor.execute(update_job_metadata(job_id, metadata))
        db_connection.commit()

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
                    row[4],
                    padding=audio_padding,
                    high_pass_frequency=high_pass_frequency,
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
                # logger.debug("{}%".format(round(index / length * 100)))
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
            path.join(
                directory,
                "{}_{}_lq{}_hq{}.xlsx".format(
                    prefix, species, threshold_min, threshold_max
                ),
            ),
            csv_list,
            header,
        )
        logger.debug("result_filepath", result_filepath)
        if result_filepath is not None:
            zip_folder_and_delete(directory, result_filepath)
            if job_id is not None:
                db_cursor.execute(update_job_progress(job_id, 100))
                db_cursor.connection.commit()
            return result_filepath
        else:
            zip_filename = "{}_{}_{}_{}.zip".format(
                directoryName, prefix, species, threshold
            )
            zip_folder_and_delete(directory, zip_filename)

            if job_id is not None:
                db_cursor.execute(update_job_progress(job_id, 100))
                db_cursor.connection.commit()
            return zip_filename, length
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
    # read command line arguments is prefix and drop flag
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default=PREFIX)
    parser.add_argument("--species", default=SPECIES)
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument("--sample_size", type=int, default=10)
    parser.add_argument("--audio_padding", type=int, default=5)
    parser.add_argument("--start_datetime", type=str, default=None)
    parser.add_argument("--end_datetime", type=str, default=None)
    parser.add_argument("--result_filepath", type=str, default=None)
    parser.add_argument("--TMP_DIRECTORY", type=str, default=None)
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
        TMP_DIRECTORY=args.TMP_DIRECTORY,
    )
