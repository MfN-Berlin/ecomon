from time import sleep
import requests
import requests
from os import path, getenv, makedirs
import os
import time
import hashlib
import wave
import json
from tools import create_metadata_dict
from uuid import uuid4

# upload file to cloud endpoint
def cloud_upload_loop_factory(files_queue, config):
    def loop():
        with open(config["uploadedFilepath"], "a") as upload_f:
            with open(config["errorFilepath"], "a") as error_f:
                while not files_queue.empty():
                    filepath = files_queue.get()

                    # create metadata file
                    metadata_dict = create_metadata_dict(filepath, config)
                    tmp_folder = path.join(config["tmp"], uuid4())
                    metadata_filepath = path.join(tmp_folder, "/metadata.json")

                    # create tmp folder for metadata file
                    makedirs(tmp_folder)

                    # save to dictionary to json file
                    with open(metadata_filepath, "w") as f:
                        json.dump(metadata_dict, f)

                    headers = {"x-access-token": getenv("BAU_TOKEN")}
                    files = {
                        "file1": open(filepath, "rb"),
                        "file2": open(metadata_filepath, "rb"),
                    }

                    try:
                        requests.post(config["url"], files=files, headers=headers)
                        upload_f.write(filepath + "\n")
                        upload_f.flush()
                    except Exception as e:
                        upload_f.write(filepath + "\n")
                        error_f.flush()
                    finally:
                        # delete tmp  file
                        os.remove(metadata_filepath)
                        os.rmdir(tmp_folder)
            # print("############ all analyzed ############")

    return loop
