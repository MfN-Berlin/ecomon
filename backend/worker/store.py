from time import sleep
from tqdm import tqdm
import wave
from typing import NamedTuple
from backend.util.db import connect_to_db, DbWorker
from os import path
from datetime import date, datetime
from pathlib import Path
from backend.util.tools import parse_filename_for_location_date_time_function_dict
import pickle
import ffmpeg
import time


def store_loop_factory(
    prefix,
    processed_files_filepath,
    all_analyzed_event,
    results_queue,
    processed_count,
    files_count,
    error_files_filepath,
    test_run=False,
    filename_parsing="ammod",
):
    # db_cursor = connect_to_db()

    def loop():

        with tqdm(
            total=files_count,
            initial=processed_count,
            desc="Analyzed",
            unit="files",
            smoothing=0.1,
        ) as progress:

            with open(processed_files_filepath, "a") as processed_f:
                with open(error_files_filepath, "a") as error_f:
                    db_worker = DbWorker(prefix)

                    while not results_queue.empty() or not all_analyzed_event.is_set():
                        if results_queue.empty():
                            sleep(1)
                            continue

                        (
                            input_filepath,
                            prediction_result_filepath,
                            error,
                        ) = results_queue.get()

                        filename = path.basename(input_filepath)
                        if error is not None:
                            raise error
                        # read audio file information
                        try:
                            metadata = ffmpeg.probe(input_filepath)["streams"][0]
                            channels = metadata["channels"]
                            duration = metadata["duration"]
                            parse_result = parse_filename_for_location_date_time_function_dict[
                                filename_parsing
                            ](
                                filename
                            )
                            # print(parse_result)
                            with open(prediction_result_filepath, "rb") as f:
                                resultDict = pickle.load(f)
                                segment_duration = resultDict["segmentDuration"]
                                start_times = resultDict["startTimes"]
                                channels_confidences = resultDict["probs"]
                                last_start = start_times[len(start_times) - 1]

                                # sanity checks if analyze worked correctly
                                if test_run is False:
                                    record_id = db_worker.add_file(
                                        input_filepath,
                                        filename,
                                        parse_result.record_datetime,
                                        duration,
                                        channels,
                                        commit=True,
                                    )
                                # add predictions
                                for channel_num, channel_confidences in zip(
                                    range(channels), channels_confidences
                                ):
                                    for start_p, confidences in zip(
                                        start_times, channel_confidences
                                    ):
                                        if test_run is False:
                                            db_worker.add_prediction(
                                                record_id,
                                                start_p,
                                                start_p + segment_duration,
                                                channel_num,
                                                confidences,
                                                commit=False,
                                            )
                                if test_run is False:
                                    # mesaure time between last prediction and end of file
                                    start = time.time()
                                    db_worker.commit()
                                    end = time.time()
                                    print(
                                        "The time of execution of above program is :",
                                        end - start,
                                    )
                                # print("store {}".format(filepath[1]))
                                # write filepath to processed to file
                                processed_f.write(input_filepath + "\n")
                                processed_f.flush()

                        except Exception as e:
                            print(
                                "Error during analysis on {} width Error:".format(
                                    filename
                                )
                            )
                            print(e)
                            error_f.write(input_filepath + "\n")
                            error_f.flush()
                        progress.update(1)

    return loop
