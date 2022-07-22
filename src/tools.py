from typing import NamedTuple
from datetime import date, datetime
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


# timedelta is in seconds
def add_time_to_datetime(dt, timedelta):
    return dt + datetime.timedelta(seconds=timedelta)


def create_metadata_dict(filepath, config):
    filename = path.basename(filepath)
    file_name_information = parse_filename_for_location_date_time()
    file_size = round(int(path.getsize(filepath)) / 1048576 * 100) / 100
    checksum = calc_checksum(filepath)

    with wave.open(filepath) as fp:
        channels = fp.getnchannels()
        sample_rate = fp.getframerate()
        frames = fp.getnframes()
        duration = round(frames / sample_rate * 100) / 100

        metadata = {
            "deviceID": config["deviceId"],
            "serialNumber": config["serialNumber"],
            "timestamp": {
                "start": file_name_information.record_time.isoformat(),
                "stop": add_time_to_datetime(
                    file_name_information.record_time, duration
                ).isoformat(),
            },
            "location": {
                "latitude": config["location"]["lat"],
                "longitude": config["location"]["lng"],
                "altitude": config["location"]["alt"],
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        config["location"]["lng"],
                        config["location"]["lat"],
                    ],
                },
            },
            "usableForResearchPurposes": False,
            "files": [
                {"fileName": filename, "fileSize": file_size, "md5Checksum": checksum,}
            ],
            "sourceFiles": [],
            "duration": duration,
            "sampleRate": sample_rate,
            "bitDepth": 16,
            "channels": channels,
            "mimeType": "audio/wav",
        }

        return metadata


def load_config(filepath):
    with open(filepath, "r") as file:
        config_dict = yaml.safe_load(file)
        config_dict["data_folder"] = os.getenv("BAI_DATA_FOLDER")
        config_dict["absolut_records_path"] = os.path.join(
            config_dict["data_folder"], config_dict["recordFolder"]
        )
        config_dict["absolut_result_path"] = os.path.join(
            config_dict["data_folder"], config_dict["resultFolder"]
        )
        config_dict["progress_cache_filepath"] = "./{}-progress.cache".format(
            config_dict["prefix"]
        )
        config_dict["error_cache_filepath"] = "./{}-error.cache".format(
            config_dict["prefix"]
        )

    return config_dict


def load_json(filepath):
    with open(filepath, "r") as read_file:
        return json.load(read_file)


def load_files_list(config, files_queue):
    print("load files list")
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

    for filepath in glob.iglob(
        config["absolut_records_path"] + "**/*.wav", recursive=True
    ):
        files_count += 1
        if processed_dict.get(filepath + "\n", False):
            # if file is already processed do not add
            continue
        files_queue.put(filepath)
    return len(lines), files_count
