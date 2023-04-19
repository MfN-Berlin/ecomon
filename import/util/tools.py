import glob
import math
import os
from typing import NamedTuple
from datetime import date, datetime, timedelta
from pathlib import Path
import hashlib
from os import path
import yaml
import wave
import json
from util.db import DbWorker

FileNameInformation = NamedTuple(
    "FileNameInformation_name_date_time",
    [("location_name", str), ("record_datetime", date),],
)


def parse_datetime(date_string):
    try:
        return datetime.strptime(date_string, "%y%m%d_%H%M%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(date_string, "%Y%m%d_%H%M%S")
    except ValueError as e:
        pass

    return datetime.strptime(date_string, "Y%m%d_%H%M%S00")


def parse_filename_inpediv(filename):
    tmp = Path(filename).stem
    parts = tmp.replace("-", "_").split(sep="_")
    record_datetime = ""

    try:
        record_datetime = parse_datetime("{}_{}".format(parts[6], parts[7]))
    except ValueError:
        try:
            record_datetime = parse_datetime("{}_{}".format(parts[7], parts[8]))
        except ValueError:
            print("Warning could not extract datetime from {}".format(filename))
            record_datetime = None
    return FileNameInformation(location_name=None, record_datetime=record_datetime,)


def parse_filename_ammod(filename):
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


parse_filename_for_location_date_time_function_dict = {
    "ammod": parse_filename_ammod,
    "inpediv": parse_filename_inpediv,
}


def load_config(filepath):
    with open(filepath, "r") as file:
        config_dict = yaml.safe_load(file)
        config_dict["data_folder"] = os.getenv("MDAS_DATA_DIRECTORY")
        record_folders = config_dict["recordFolder"]
        # if recordFolders is a string, convert it to a list
        if isinstance(record_folders, str):
            record_folders = [record_folders]
        absolute_records_path = []
        for record_folder in record_folders:
            absolute_records_path.append(
                os.path.join(config_dict["data_folder"], record_folder)
            )
        config_dict["absolute_records_path"] = absolute_records_path
        config_dict["absolute_result_path"] = os.path.join(
            config_dict["data_folder"], config_dict["resultFolder"]
        )
        config_dict["progress_cache_filepath"] = "./cache/{}-progress.cache".format(
            config_dict["prefix"]
        )
        config_dict["error_cache_filepath"] = "./cache/{}-error.cache".format(
            config_dict["prefix"]
        )
        config_dict["basePort"] = (
            int(config_dict["basePort"]) if ("basePort" in config_dict) else 9000
        )
        config_dict["analyzeThreads"] = (
            int(config_dict["analyzeThreads"])
            if "analyzeThreads" in config_dict
            else int(os.getenv("MDAS_ANALYZE_THREADS", 1))
        )
        config_dict["allThreadsUseSamePort"] = (
            config_dict["allThreadsUseSamePort"]
            if "allThreadsUseSamePort" in config_dict
            else False
        )
        config_dict["transformModelOutput"] = (
            config_dict["transformModelOutput"]
            if "transformModelOutput" in config_dict
            else False
        )
        config_dict["repeats"] = (
            int(config_dict["repeats"]) if "repeats" in config_dict else 10
        )
        config_dict["modelOutputStyle"] = (
            config_dict["modelOutputStyle"]
            if "modelOutputStyle" in config_dict
            else None
        )
        config_dict["onlyAnalyze"] = (
            config_dict["onlyAnalyze"] if "onlyAnalyze" in config_dict else False
        )

    return config_dict


def load_json(filepath):
    with open(filepath, "r") as read_file:
        return json.load(read_file)


def load_files_list(config, files_queue,list_of_files_in_db, retry_corrupted_files=False, prefix=None, ):
    lines = []
    files_count = 0
    if(retry_corrupted_files):
        print("Retry corrupted files with prefix: {}".format(prefix))
        db_worker = DbWorker(prefix)
       
        files = db_worker.get_corrupted_files()
        print("Found {} corrupted files".format(len(files)))

        for row in files:
            files_queue.put(row[0])
            files_count += 1
        # exit program
  
        return 0, files_count
    else:

        processed_dict = {}
        
        for filepath in list_of_files_in_db:
            processed_dict[filepath] = True

        # print(config["absolute_records_path"] + "**/*.{}".format(config["fileEnding"][0]))
        files = []
        absolute_paths = config["absolute_records_path"]
        # if absolute_paths is not a list, make it one
        if not isinstance(absolute_paths, list):
            absolute_paths = [absolute_paths]

        for absolute_path in absolute_paths:
            for ext in config["fileEnding"]:
                files.extend(
                    glob.iglob(absolute_path + "**/*.{}".format(ext), recursive=True,)
                )
        print("Found raw files {}".format(len(files)))
        for filepath in files:
            files_count += 1
            if processed_dict.get(filepath, False):
                # if file is already processed do not add
                continue
            # check if is files_queue is alist and append filepath
            # if not, add filepath to files_queue
            if isinstance(files_queue, list):
                files_queue.append(filepath)
            else:
                files_queue.put(filepath)
    return len(list_of_files_in_db), files_count

