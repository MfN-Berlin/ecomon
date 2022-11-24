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

FileNameInformation = NamedTuple(
    "FileNameInformation_name_date_time",
    [("location_name", str), ("record_datetime", date),],
)


def calc_checksum(filename, hash_factory=hashlib.md5, chunk_num_blocks=128):
    h = hash_factory()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_num_blocks * h.block_size), b""):
            h.update(chunk)
    return h.hexdigest()


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


# timedelta is in seconds
def add_time_to_datetime(dt, delta):
    seconds = int(math.floor(delta))
    milliseconds = int(round((delta - seconds) * 1000))
    return dt + timedelta(seconds=seconds, milliseconds=milliseconds)


def load_config(filepath):
    with open(filepath, "r") as file:
        config_dict = yaml.safe_load(file)
        config_dict["data_folder"] = os.getenv("BAI_DATA_DIRECTORY")
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
            else int(os.getenv("BAI_ANALYZE_THREADS", 1))
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

    return config_dict


def load_json(filepath):
    with open(filepath, "r") as read_file:
        return json.load(read_file)


def load_files_list(config, files_queue):
    lines = []

    files_count = 0
    try:
        with open(config["progress_cache_filepath"], "r") as processed_f:
            lines = processed_f.readlines()
    except FileNotFoundError as e:
        # no cached process file exist -> it is a new run
        pass

    processed_dict = {}
    for filepath in lines:
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

    for filepath in files:
        files_count += 1
        if processed_dict.get(filepath + "\n", False):
            # if file is already processed do not add
            continue
        files_queue.put(filepath)
    return len(lines), files_count


def parse_boolean(value):
    value = value.lower()

    if value in ["true", "yes", "y", "1", "t"]:
        return True
    elif value in ["false", "no", "n", "0", "f"]:
        return False

    return False


def species_row_to_name(string):
    tmp = string[0].upper() + string[1:]
    tmp = tmp.replace("_", " ")
    return tmp
