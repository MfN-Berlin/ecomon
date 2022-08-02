import queue
import threading
from time import sleep
from dotenv import load_dotenv
import requests
import requests
from os import path, getenv, makedirs
import os
import json
from tools import create_metadata_dict, load_config, load_files_list
from uuid import uuid4

# upload file to cloud endpoint
def cloud_upload_loop_factory(config, files_queue):
    def loop():
        with open(config["uploadedFilepath"], "a") as upload_f:
            with open(config["errorFilepath"], "a") as error_f:
                while not files_queue.empty():
                    filepath = files_queue.get()

                    # create metadata file
                    metadata_dict = create_metadata_dict(filepath, config)
                    tmp_folder = path.join(config["tmp"], uuid4().hex)
                    metadata_filepath = path.join(tmp_folder, "metadata.json")

                    # create tmp folder for metadata file
                    makedirs(tmp_folder)

                    # save to dictionary to json file
                    with open(metadata_filepath, "w+") as f:
                        json.dump(metadata_dict, f)

                    headers = {"x-access-token": getenv("BAU_TOKEN")}
                    files = {
                        "file1": open(filepath, "rb"),
                        "file2": open(metadata_filepath, "rb"),
                    }

                    url = path.join(config["baseUrl"], "/metadata")
                    try:
                        requests.post(url, files=files, headers=headers)
                        upload_f.write(filepath + "\n")
                        upload_f.flush()
                    except Exception as e:

                        error_f.write(filepath + "\n")
                        error_f.flush()
                    finally:
                        # delete tmp  file
                        os.remove(metadata_filepath)
                        os.rmdir(tmp_folder)
            # print("############ all analyzed ############")

    return loop


def main():
    load_dotenv()  # load environment variables from .env
    files_queue = queue.Queue()

    CONFIG_FILEPATH = "./config.yaml"
    config = load_config(CONFIG_FILEPATH)
    processed_count, files_count = load_files_list(config, files_queue)

    # Created the Threads
    upload_threads = [
        threading.Thread(
            target=cloud_upload_loop_factory(config["cloudUpload"], files_queue)
        )
    ]

    print("start uploading folder: {}".format(config["recordFolder"]))
    for thread in upload_threads:
        thread.start()

    for thread in upload_threads:
        thread.join()


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
