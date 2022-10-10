from datetime import timedelta
import glob
import hashlib
import math
import queue
import threading
from time import sleep
from turtle import width
import wave
from dotenv import load_dotenv
import requests
import requests
from os import path, getenv, makedirs
import os
import json
import pytz
import pickle
from urllib.parse import urljoin
from datetime import datetime
import numpy as np
from uuid import uuid4


# timedelta is in seconds
def add_time_to_datetime(dt, delta):
    seconds = int(math.floor(delta))
    milliseconds = int(round((delta - seconds) * 1000))
    return dt + timedelta(seconds=seconds, milliseconds=milliseconds)


def calc_checksum(filename, hash_factory=hashlib.md5, chunk_num_blocks=128):
    h = hash_factory()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_num_blocks * h.block_size), b""):
            h.update(chunk)
    return h.hexdigest()


def get_datetime_from_filename(filename, timezone):
    parts = filename.split(".")[0].split("_")
    record_datetime = datetime.strptime(
        "{}_{}".format(parts[1], parts[2]), "%Y%m%d_%H%M%S"
    )
    aware = pytz.timezone(timezone).localize(record_datetime, is_dst=None)
    return aware


def create_metadata_dict(filepath, device_information, timezone="UTC"):
    filename = path.basename(filepath)

    file_size = round(int(path.getsize(filepath)) / 1048576 * 100) / 100
    checksum = calc_checksum(filepath)
    record_datetime = get_datetime_from_filename(filename, timezone)
    with wave.open(filepath) as fp:
        channels = fp.getnchannels()
        sample_rate = fp.getframerate()
        frames = fp.getnframes()
        duration = round(frames / sample_rate)

        metadata = {
            "deviceID": device_information["deviceId"],
            "serialNumber": device_information["serialNumber"],
            "timestamp": {
                "start": record_datetime.isoformat(),
                "stop": add_time_to_datetime(record_datetime, duration).isoformat(),
            },
            "location": {
                "latitude": device_information["location"]["latitude"],
                "longitude": device_information["location"]["longitude"],
                "altitude": device_information["location"]["altitude"],
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        device_information["location"]["longitude"],
                        device_information["location"]["latitude"],
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


def get_refresh_token(base_url, current_token):
    url = urljoin(base_url, "token/refresh")
    try:
        result = requests.get(
            url, headers={"x-access-token": current_token, "accept": "application/json"}
        )
        result_data = result.json()
        refresh_token = result_data["refreshToken"]
        token = result_data["token"]
        expiry = result_data["expiry"]
        return refresh_token, token, expiry

    except Exception as e:
        raise e


# upload file to cloud endpoint
def raw_data_upload(
    filepath,
    device_information,
    base_url,
    access_token,
    timezone="utc",
    tmp_directory="./tmp",
):
    # create metadata file
    metadata_dict = create_metadata_dict(filepath, device_information)
    tmp_folder = path.join(tmp_directory, uuid4().hex)
    filename = path.basename(filepath)
    metadata_filepath = path.join(tmp_folder, "{}_metadata.json".format(filename))

    # create tmp folder for metadata file
    makedirs(tmp_folder)

    # save to dictionary to json file
    with open(metadata_filepath, "w+") as f:
        json.dump(metadata_dict, f)

    headers = {"x-access-token": access_token}
    files = {
        "file1": open(filepath, "rb"),
        "file2": open(metadata_filepath, "rb"),
    }
    # join urls

    url = urljoin(base_url, "metadata")
    try:
        result = requests.post(url, files=files, headers=headers)
        os.remove(metadata_filepath)
        os.rmdir(tmp_folder)
        return result

    except Exception as e:
        os.remove(metadata_filepath)
        os.rmdir(tmp_folder)
        raise e


def get_detected_species(
    pickle_dict, threshold_dict, parent_filename, default_threshold=0.9
):
    detected_species = []
    channel_values = pickle_dict["probs"]
    max_segments_confidences = np.max(channel_values, axis=0)
    max_species_confidences = np.max(max_segments_confidences, axis=0)

    detected_species = []
    for index, value in enumerate(max_species_confidences):
        threshold = threshold_dict.get(index, default_threshold)
        if value > threshold:
            detected_species.append(
                {
                    "name": pickle_dict["classNamesScientific"][index],
                    "confidence": value.item(),
                }
            )
    return {
        "default_threshold": default_threshold,
        "thresholds": threshold_dict,
        "detected_species": detected_species,
        "fileName": parent_filename,
    }


def pickle_to_json(
    raw_prediction, filename, model_name, model_version,
):
    channels = []
    start_times = raw_prediction["startTimes"]
    segment_duration = raw_prediction["segmentDuration"]

    for channel in raw_prediction["probs"]:
        predictions = []
        for prediction_idx, prediction in enumerate(channel):
            predictions.append(
                {
                    "startTime": start_times[prediction_idx],
                    "endTime": start_times[prediction_idx] + segment_duration,
                    "predictions": {"probabilities": prediction.tolist()},
                }
            )
        channels.append(predictions)

    json_dict = {
        "classIds": raw_prediction["classNamesScientific"],
        "detectedClassIds": [],
        "channels": channels,
        "fileName": filename,
        "modelName": model_name,
        "modelVersion": model_version,
    }
    return json_dict


def processed_data_upload(
    filename,
    result_directory,
    base_url,
    access_token,
    model_name,
    model_version,
    threshold_dict,
    timezone="utc",
    tmp_directory="./tmp",
):
    filename_no_ext = path.splitext(filename)[0]
    raw_filepath = path.join(result_directory, "{}.pkl".format(filename_no_ext))

    with open(raw_filepath, "rb") as f:
        raw_prediction = pickle.load(f)
    json_dict = pickle_to_json(raw_prediction, filename, model_name, model_version)
    detected_species = get_detected_species(
        raw_prediction,
        threshold_dict,
        "{}_prediction.json".format(filename_no_ext),
        default_threshold=0.9,
    )
    tmp_folder = path.join(tmp_directory, uuid4().hex)
    makedirs(tmp_folder)
    json_prediction_filepath = path.join(
        tmp_folder, "{}_prediction.json".format(filename_no_ext)
    )
    json_species_filepath = path.join(
        tmp_folder, "{}_species_list.json".format(filename_no_ext)
    )
    # save json_dict to json file
    with open(json_prediction_filepath, "w+") as f:
        json.dump(json_dict, f)
        pass
    with open(json_species_filepath, "w+") as f:
        json.dump(detected_species, f)
        pass

    pass


def load_files(directory, ext="wav"):
    files = list(glob.iglob(directory + "**/*.{}".format(ext), recursive=True,))
    return files


record_directory = "/net/mfnstore-lin/export/tsa_transfer/AudioData/AMMOD/BRITZ02/"
result_directory = (
    "/net/mfnstore-lin/export/tsa_transfer/Results/birdid-europe254-2103/AMMOD/BRITZ02"
)


TIMEZONE = "Europe/Berlin"
DEVICE_INFO = {
    "deviceId": 7977,
    "serialNumber": "002",
    "location": {
        "latitude": 52.878001,
        "longitude": 13.832996,
        "altitude": 50,
        "geometry": {"type": "Point", "coordinates": [52.878001, 13.832996],},
    },
}
MODEL_INFO = {
    "modelName": "birdid-europe254-2103",
    "modelVersion": "1.0.0",
}

THRESHOLD_DICT = {
    "Fringilla coelebs": 0.5,
    "Erithacus rubecula": 0.96,
    "Turdus merula": 0.8,
}

DEFAULT_THRESHOLD = 0.9

# access_token:
# 72642e7045267840388ac839ba47
# refresh_token:
# b505df9b0a30d55cb2c5a34acc9f
# expiry:
# 2022-10-05T17:42:16+02:00
BASE_URL = "https://ammod.gfbio.dev/api/v1/"
ACCESS_TOKEN = "72642e7045267840388ac839ba47"
REFRESH_TOKEN = "b505df9b0a30d55cb2c5a34acc9f"


def main():
    load_dotenv()  # load environment variables from .env
    files_queue = queue.Queue()
    files = load_files(record_directory)
    # create hash of string to save progress
    hash_object = hashlib.md5(record_directory.encode("utf-8"))
    hex_dig = hash_object.hexdigest()
    uploaded_file_path = path.join(hex_dig + ".uploaded.txt")
    error_file_path = path.join(hex_dig + ".error.txt")
    # read all lines from text file into dict
    uploaded_files = {}
    error_files = {}
    if path.exists(uploaded_file_path):
        with open(uploaded_file_path, "r") as f:
            for line in f.readlines():

                uploaded_files[line.strip()] = True

    # open text file for adding lines

    with open(uploaded_file_path, "a") as uploaded_f:
        with open(error_file_path, "a") as error_f:
            access_token = ACCESS_TOKEN
            refresh_token = REFRESH_TOKEN
            for file in files:
                if file.strip() in uploaded_files:
                    continue
                else:
                    # result = raw_data_upload(
                    #     line.strip(),
                    #     DEVICE_INFO,
                    #     BASE_URL,
                    #     access_token,
                    #     timezone=TIMEZONE,
                    # )
                    processed_data_upload(
                        path.basename(file),
                        result_directory,
                        BASE_URL,
                        access_token,
                        MODEL_INFO["modelName"],
                        MODEL_INFO["modelVersion"],
                        THRESHOLD_DICT,
                        timezone=TIMEZONE,
                    )

                    # refresh token
                    refresh_token, access_token, expiry = get_refresh_token(
                        BASE_URL, refresh_token
                    )

                    pass

    # print(uploaded_files)


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
