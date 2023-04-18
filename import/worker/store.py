import os
from time import sleep
from tqdm import tqdm
from util.db import connect_to_db, DbWorker
from os import path
from util.tools import parse_filename_for_location_date_time_function_dict
import pickle
import ffmpeg
import time
import numpy as np


# calc max pairwise of n dimensional list


def store_loop_factory(
    prefix,
    processed_files_filepath,
    error_files_filepath,
    all_analyzed_event,
    results_queue,
    processed_count,
    files_count,
    test_run=False,
    filename_parsing="ammod",
    timezone=None,
    index_to_name=None,
    only_analyze=False,
    retry_corrupted_files=False,

):
    # db_cursor = connect_to_db()
    def loop():
        print("Starting store loop")
        with tqdm(
            total=files_count,
            initial=processed_count,
            desc="Analyzed",
            unit="files",
            smoothing=0.1,

        ) as progress:
            if only_analyze is False:
                db_worker = DbWorker(prefix)
            with open(processed_files_filepath, "a") as processed_f:
                if path.exists(error_files_filepath):
                    os.remove(error_files_filepath)
                with open(error_files_filepath, "a+") as error_f:

                    # for species in species_index_list:
                    #     print("Dropping index to {}".format(species))
                    #     try:
                    #         db_worker.drop_index(prefix, species)
                    #     except Exception as e:
                    #         print(e)
                    #         db_worker.rollback()

                    while (
                        # False
                        not results_queue.empty()
                        or not all_analyzed_event.is_set()
                    ):
                        if results_queue.empty():
                            sleep(1)
                            progress.set_postfix(store_idling="Yes")
                            continue
                        else:
                            progress.set_postfix(store_idling="No")
                        (
                            input_filepath,
                            prediction_result_filepath,
                            error,
                            port,
                        ) = results_queue.get()

                        filename = path.basename(input_filepath)
                        if error is not None:
                            raise error
                        # read audio file information
                        try:
                            if only_analyze:
                                # open procdessed file path
                                with open(prediction_result_filepath, "rb") as f:
                                    processed_f.write(input_filepath + "\n")
                                    processed_f.flush()
                                    progress.update(1)
                                    continue

                            # check if file exists
                            if not path.exists(input_filepath):
                                raise Exception(
                                    "File {} does not exist".format(input_filepath)
                                )
                            parse_result = parse_filename_for_location_date_time_function_dict[
                                filename_parsing
                            ](
                                filename
                            )
                            # print(parse_result)
                            record_datetime = (
                                parse_result.record_datetime
                                if timezone is None
                                else timezone.localize(parse_result.record_datetime)
                            )
                            try:
                                metadata = ffmpeg.probe(input_filepath)["streams"][0]
                                channels = metadata["channels"]
                                duration = metadata["duration"]
                            except Exception as e:

                                if test_run is False:
                                    if(retry_corrupted_files):
                                        record_id = db_worker.update_record(
                                            input_filepath,
                                            0,
                                            0,
                                            corrupted=True,
                                            commit=True,
                                        )
                                    else:
                                        record_id = db_worker.add_file(
                                            input_filepath,
                                            filename,
                                            record_datetime,
                                            0,
                                            0,
                                            commit=True,
                                            corrupted=True,
                                        )
                                # write filepath to processed to file
                                processed_f.write(input_filepath + "\n")
                                processed_f.flush()
                                progress.update(1)
                                continue

                            with open(prediction_result_filepath, "rb") as f:
                                resultDict = pickle.load(f)
                                segment_duration = resultDict["segmentDuration"]
                                start_times = resultDict["startTimes"]
                                channels_segments_confidences = resultDict["probs"]

                                # sanity checks if analyze worked correctly
                                record_id = 0
                                if test_run is False:
                                    if(retry_corrupted_files):
                                        record_id = db_worker.update_record(
                                            input_filepath,
                                            duration,
                                            channels,
                                            corrupted=False,
                                            commit=False,
                                        )
                                       
                                    else: 
                                        record_id = db_worker.add_file(
                                            input_filepath,
                                            filename,
                                            record_datetime,
                                            duration,
                                            channels,
                                            commit=False,
                                        )

                                # add predictions

                                # for channel_num, segments_confidences in zip(
                                #     range(channels), channels_segments_confidences
                                # ):
                                #     for start_p, confidences in zip(
                                #         start_times, segments_confidences
                                #     ):
                                #         if test_run is False:
                                #             db_worker.add_prediction(
                                #                 record_id,
                                #                 start_p,
                                #                 start_p + segment_duration,
                                #                 "ch_{}".format(channel_num),
                                #                 confidences,
                                #                 commit=False,
                                #             )

                                max_segements_confidences = np.max(
                                    channels_segments_confidences, axis=0
                                )

                                for start_p, confidences in zip(
                                    start_times, max_segements_confidences
                                ):
                                    # add max_confidences
                                    if test_run is False:
                                        db_worker.add_prediction(
                                            record_id,
                                            start_p,
                                            start_p + segment_duration,
                                            "ch_max",
                                            confidences,
                                            commit=False,
                                            index_to_name=index_to_name,
                                        )

                                if test_run is False:
                                    # mesaure time between last prediction and end of file
                                    start = time.time()
                                    db_worker.commit()

                                    end = time.time()
                                    # print(
                                    #     "The time of execution of above program is :",
                                    #     end - start,
                                    # )
                                else:
                                    db_worker.rollback()
                                # print("store {}".format(filepath[1]))
                                # write filepath to processed to file
                                processed_f.write(input_filepath + "\n")
                                processed_f.flush()

                        except Exception as e:
                            # if you want to ignore duplicate entries uncomment the following line
                            # if "Duplicate entry" in str(e):
                            #     processed_f.write(input_filepath + "\n")
                            #     processed_f.flush()
                            #     continue
                            print(
                                "Store Worker: {} error: Error during analysis on {} width Error:".format(
                                    port, filename
                                )
                            )
                            error_f.write("{}, {}".format(input_filepath, e) + "\n")
                            error_f.flush()
                            if only_analyze is False:
                                db_worker.rollback()
                        progress.update(1)
                    # now add index to species columns
                    # check if error file has entries
                    error_f.seek(0)
                    error_file_lines = error_f.readlines()
                    # check if one line of  error_file_lines   inlcudes ffprobe error
                    found_analyze_error = False
                    for line in error_file_lines:
                        if "ffprobe error" not in line:
                            found_analyze_error = True
                            print("found different error")

                    # if not found_analyze_error:
                    #     print("Start adding index to species columns")
                    #     for species in species_index_list:
                    #         print("Adding index to {}".format(species))
                    #         try:
                    #             db_worker.add_index(prefix, species)
                    #             print("Finished adding index to species columns")
                    #         except Exception as e:
                    #             print(e)
                    #             db_worker.rollback()
                    # else:
                    #     print("Error file has more than 10 entries. Not adding index")

    return loop
