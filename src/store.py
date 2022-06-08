from time import sleep
from tqdm import tqdm
import wave
from typing import NamedTuple
from db import connect_to_db, DbWorker
from os import path
from datetime import date, datetime
from pathlib import Path

FileNameInformation = NamedTuple(
    "FileNameInformation_name_date_time",
    [("location_name", str), ("record_datetime", date),],
)


def parse_datetime(date_string):
    try:
        return datetime.strptime(date_string, "%Y%m%d_%H%M%S")
    except ValueError as e:
        print(e)
        pass
    try:
        return datetime.strptime(date_string, "%y%m%d_%H%M%S")
    except ValueError:
        pass
    return datetime.strptime(date_string, "Y%m%d_%H%M%S00")


def parse_filename_for_location_date_time(filename):
    tmp = Path(filename).stem
    parts = tmp.replace("-", "_").split(sep="_", maxsplit=1)

    location_name = parts[0]
    record_datetime = ""

    if len(parts[1].split(sep="_")) > 2:
        subparts = parts[1].split(sep="_")
        try:
            record_datetime = parse_datetime("{}_{}".format(subparts[0], subparts[1]))
        except ValueError:
            print("Warning could not extract datetime from {}".format(filename))
            record_datetime = None

    else:
        try:
            record_datetime = parse_datetime(parts[1])
        except ValueError:
            print("Warning could not extract datetime from {}".format(filename))
            record_datetime = None
    return FileNameInformation(
        location_name=location_name, record_datetime=record_datetime,
    )


def store_loop_factory(
    prefix,
    processed_files_filepath,
    all_analyzed_event,
    results_queue,
    processed_count,
    files_count,
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
                db_worker = DbWorker(prefix)

                while not results_queue.empty() or not all_analyzed_event.is_set():
                    if results_queue.empty():
                        sleep(1)
                        continue
                    input_filepath, prediction_result_filepath = results_queue.get()

                    filename = path.basename(input_filepath)
                    # read audio file information
                    with wave.open(input_filepath) as fp:
                        channels = fp.getnchannels()
                        sample_rate = fp.getframerate()
                        frames = fp.getnframes()
                        duration = round(frames / sample_rate * 100) / 100
                    parse_result = parse_filename_for_location_date_time(filename)

                    record_id = db_worker.add_file(
                        input_filepath,
                        filename,
                        parse_result.record_datetime,
                        duration,
                        channels,
                        commit=True,
                    )
                    # add predictions
                    for i in range(int(duration) - 5):
                        db_worker.add_prediction(
                            record_id, i, i + 4, 0, range(254), commit=False
                        )
                    db_worker.commit()
                    # print("store {}".format(filepath[1]))
                    # write filepath to processed to file
                    processed_f.write(input_filepath + "\n")
                    processed_f.flush()
                    progress.update(1)
                    sleep(0.1)

    return loop
