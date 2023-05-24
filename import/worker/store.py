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
import pytz


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
    debug=False,
):
    if(debug):
        # print all intial parameters   
        print(f'Store: prefix: {prefix}')
        print(f'Store: processed_files_filepath: {processed_files_filepath}')
        print(f'Store: error_files_filepath: {error_files_filepath}')
        print(f'Store: all_analyzed_event: {all_analyzed_event}')
        print(f'Store: results_queue: {results_queue}')
        print(f'Store: processed_count: {processed_count}')
        print(f'Store: files_count: {files_count}')
        print(f'Store: test_run: {test_run}')
        print(f'Store: filename_parsing: {filename_parsing}')
        print(f'Store: timezone: {timezone}')
        print(f'Store: index_to_name: {index_to_name}')
        print(f'Store: only_analyze: {only_analyze}')
        print(f'Store: retry_corrupted_files: {retry_corrupted_files}')
        print(f'Store: debug: {debug}')

    # db_cursor = connect_to_db()
    def loop():
        if(debug):
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
                    while (
                        # False
                        not results_queue.empty()
                        or not all_analyzed_event.is_set()
                    ):

                        if results_queue.empty():
                            progress.set_postfix(
                                idle=f'{"*" if all_analyzed_event.is_set() else "_"}|*'
                            )
                            sleep(1)
                            continue
                        else:
                            progress.set_postfix(
                                idle=f'{"*" if all_analyzed_event.is_set() else "_"}|_'
                            )
                        (
                            input_filepath,
                            prediction_result_filepath,
                            error,
                            port,
                        ) = results_queue.get()
                        if(debug):
                            print(f'Store: Begin to store file:{input_filepath}')
                        filename = path.basename(input_filepath)
                        if error is not None:
                            if(debug):
                                print(f'Store: Found analyze error of file:{input_filepath}: {str(error)}')
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
                                if(debug):
                                    print(f'Store: file does not exist {input_filepath}')
                                raise Exception(
                                    f"File {input_filepath} does not exist"
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
                                if(debug):
                                    print(f'Store: filename meta error: ${str(e)}')

                                if test_run is False:
                                    if retry_corrupted_files:
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
                                    if retry_corrupted_files:
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
                                  
                                else:
                                    db_worker.rollback()
                                if(debug):
                                    print(f"Store: input_filepath: {input_filepath}")
                                # write filepath to processed to file
                                processed_f.write(input_filepath + "\n")
                                processed_f.flush()

                        except Exception as e:
                            # if you want to ignore duplicate entries uncomment the following line
                            # if "Duplicate entry" in str(e):
                            #     processed_f.write(input_filepath + "\n")
                            #     processed_f.flush()
                            #     continue
                            if(debug):
                                print(
                                    f'Store: on Port {port} error: Error during analysis on {filename} width Error: {str(e)}'
                                )
                            error_f.write(f"{input_filepath}, {str(e)}" + "\n")
                            error_f.flush()
                            if only_analyze is False:
                                db_worker.rollback()
                        progress.update(1)
                    # now add index to species columns
                    # check if error file has entries

  
            db_worker.close()

    return loop
