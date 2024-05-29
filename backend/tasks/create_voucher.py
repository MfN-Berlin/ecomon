from typing import List, Optional
from os import path
from dotenv import load_dotenv
from uuid import uuid4
import os
import shutil
import json
from util.excel import write_execl_file

from util.db import connect_to_db
from util.tools import s_to_time, first_letter_to_upper_case, zip_folder_and_delete
from util.audio import extract_part_from_audio_file_by_start_and_end_time
from sql.query import (
    get_job_by_id,
    update_job_failed,
    update_job_progress,
    update_job_metadata,
    update_job_status,
    get_prediction_max_sample,
    get_prediction_file_distinct_max_sample,
)
from logging import getLogger
logger = getLogger(__name__)


def create_voucher(
    collection: str,
    species_list: List[str],
    sample_size: int = 10,
    audio_padding: int = 5,
    result_filepath: Optional[str] = None,
    job_id: Optional[str] = None,
    high_pass_frequency: int = 0,
    tmp_directory: Optional[str] = path.join(os.getcwd(), "tmp"),
    results_directory: Optional[str] = path.join(os.getcwd(), "web_results"),
) -> None:
    # logger.debug("High pass frequency: ", high_pass_frequency)
    load_dotenv()
    db_connection = connect_to_db()
    db_cursor = db_connection.cursor()
    directoryName = uuid4().hex
    directory = path.join(tmp_directory, directoryName)
    os.makedirs(directory, exist_ok=True)

    if result_filepath is None:
        result_filepath = f"{directoryName}_{collection}_vouchers.zip"

    result_filename = path.basename(result_filepath)

    # if results_directory does not exist create it
    if not path.exists(results_directory):
        os.makedirs(results_directory, exist_ok=True)

    try:
        if job_id is not None:
            db_cursor.execute(get_job_by_id(job_id))
            job = db_cursor.fetchone()
            metadata = json.loads(job[4])
            metadata["samples"] = sample_size
            metadata["filename"] = result_filename
            metadata["filepath"]: path.join(results_directory, result_filepath)
            db_cursor.execute(update_job_status(job_id, "running"))
            db_cursor.execute(update_job_metadata(job_id, metadata))
            db_connection.commit()
        progress = 0
        inter_species_progress = 100 / len(species_list)

        for species_index, species in enumerate(species_list):
            query = get_prediction_file_distinct_max_sample(
                collection,
                species,
                sample_size,
            )
            logger.debug(query)
            db_cursor.execute(query)
            result = db_cursor.fetchall()
            entries_length = len(result)

            # 0   r.filepath,
            # 1   r.record_datetime,
            # 2   r.filename,
            # 3   p.start_time,
            # 4   p.end_time,
            # 5   r.duration,
            # 6   p.channel,
            # 7   p.{species}
            csv_list = []
            for row_index, row in enumerate(result):
                filepath = row[0]
                filename = path.basename(filepath)
                start = float(row[3])
                end = float(row[4])
                record_datetime = row[1]
                duration = row[5]
                channel = row[6]
                confidence = row[7]

                [stem, ext] = path.splitext(filename)

                out_filename = "{stem}_S{start}_E{end}{ext}".format(
                    stem=stem, start=s_to_time(start), end=s_to_time(end), ext=ext
                )
                out_filepath = path.join(directory, out_filename)
                # check if file not exists

                if not path.exists(path.join(directory, out_filename)):
                    extract_part_from_audio_file_by_start_and_end_time(
                        filepath,
                        out_filepath,
                        start,
                        end,
                        duration,
                        padding=audio_padding,
                        high_pass_frequency=high_pass_frequency,
                    )
                # logger.debug("out_filepath", out_filepath)

                tmp = {
                    "species": first_letter_to_upper_case(species).replace("_", " "),
                    "filename": out_filename,
                    "record_datetime": record_datetime,
                    "start_time": start,
                    "end_time": end,
                    "duration": duration,
                    "channel": channel,
                    "confidence": confidence,
                    "audio_padding": audio_padding,
                }
                csv_list.append(tmp)
                progress = round(
                    inter_species_progress * species_index
                    + (inter_species_progress / entries_length) * row_index
                )

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
                    "{}_{}.xlsx".format(collection, species),
                ),
                csv_list,
                header,
            )

        zip_folder_and_delete(directory, path.join(results_directory, result_filepath))
        if job_id is not None:
            db_cursor.execute(update_job_progress(job_id, 100))
            db_cursor.execute(update_job_status(job_id, "done"))
            db_cursor.connection.commit()
        return result_filepath

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
