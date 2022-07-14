from time import sleep
import threading, queue
import yaml
import glob
from dotenv import load_dotenv
from analyze import analyze_loop_factory
from store import store_loop_factory
from db import init_db
import json
import os

load_dotenv()  # load environment variables from .env

files_queue = queue.Queue()
results_queue = queue.Queue()
all_analyzed_event = threading.Event()

CONFIG_FILEPATH = "./config.yaml"


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


config = load_config(CONFIG_FILEPATH)


def load_files_list():
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


def load_json(filepath):
    with open(filepath, "r") as read_file:
        return json.load(read_file)


index_to_name = load_json(config["indexToNameFile"])

init_db(config["prefix"], index_to_name)
# load_file_list
processed_count, files_count = load_files_list()

# Created the Threads
analyze_threads = [
    threading.Thread(
        target=analyze_loop_factory(
            files_queue,
            results_queue,
            all_analyzed_event,
            9000,
            config["data_folder"],
            config["resultFolder"],
        )
    ),
    # threading.Thread(
    #     target=analyze_loop_factory(
    #         files_queue,
    #         results_queue,
    #         all_analyzed_event,
    #         9001,
    #         config["data_folder"],
    #         config["resultFolder"],
    #     )
    # ),
    # threading.Thread(
    #     target=analyze_loop_factory(
    #         files_queue,
    #         results_queue,
    #         all_analyzed_event,
    #         9002,
    #         config["data_folder"],
    #         config["resultFolder"],
    #     )
    # ),
    # threading.Thread(
    #     target=analyze_loop_factory(
    #         files_queue,
    #         results_queue,
    #         all_analyzed_event,
    #         9003,
    #         config["data_folder"],
    #         config["resultFolder"],
    #     )
    # ),
    # threading.Thread(
    #     target=analyze_loop_factory(
    #         files_queue,
    #         results_queue,
    #         all_analyzed_event,
    #         9004,
    #         config["data_folder"],
    #         config["resultFolder"],
    #     )
    # ),
    # threading.Thread(
    #     target=analyze_loop_factory(
    #         files_queue,
    #         results_queue,
    #         all_analyzed_event,
    #         9005,
    #         config["data_folder"],
    #         config["resultFolder"],
    #     )
    # ),
    # threading.Thread(
    #     target=analyze_loop_factory(
    #         files_queue,
    #         results_queue,
    #         all_analyzed_event,
    #         9006,
    #         config["data_folder"],
    #         config["resultFolder"],
    #     )
    # ),
    # threading.Thread(
    #     target=analyze_loop_factory(
    #         files_queue,
    #         results_queue,
    #         all_analyzed_event,
    #         9007,
    #         config["data_folder"],
    #         config["resultFolder"],
    #     )
    # ),
    # threading.Thread(
    #     target=analyze_loop_factory(
    #         files_queue,
    #         results_queue,
    #         all_analyzed_event,
    #         9008,
    #         config["data_folder"],
    #         config["resultFolder"],
    #     )
    # ),
]


store_thread = threading.Thread(
    target=store_loop_factory(
        config["prefix"],
        config["progress_cache_filepath"],
        all_analyzed_event,
        results_queue,
        processed_count,
        files_count,
        config["error_cache_filepath"],
    )
)

# Started the threads
print("Start analyze_thread")
for thread in analyze_threads:
    thread.start()

print("Start store_thread")
store_thread.start()


# Joined the threads
for thread in analyze_threads:
    thread.join()

store_thread.join()

