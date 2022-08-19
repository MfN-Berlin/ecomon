from time import sleep
import threading, queue
import yaml
import glob
from dotenv import load_dotenv
from backend.worker.analyze import analyze_loop_factory
from backend.worker.store import store_loop_factory
from backend.util.db import init_db
from backend.util.tools import (
    load_config,
    load_files_list,
    load_json,
    load_files_list,
    count_entries_in_sql_table,
)


load_dotenv()  # load environment variables from .env

files_queue = queue.Queue()
results_queue = queue.Queue()
all_analyzed_event = threading.Event()

CONFIG_FILEPATH = "./config.yaml"


config = load_config(CONFIG_FILEPATH)


index_to_name = load_json(config["indexToNameFile"])

init_db(config["prefix"], index_to_name)
# load_file_list
processed_count, files_count = load_files_list(config, files_queue)

print("Files found {} allready processed {}".format(files_count, processed_count))
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
    threading.Thread(
        target=analyze_loop_factory(
            files_queue,
            results_queue,
            all_analyzed_event,
            9001,
            config["data_folder"],
            config["resultFolder"],
        )
    ),
    threading.Thread(
        target=analyze_loop_factory(
            files_queue,
            results_queue,
            all_analyzed_event,
            9002,
            config["data_folder"],
            config["resultFolder"],
        )
    ),
    threading.Thread(
        target=analyze_loop_factory(
            files_queue,
            results_queue,
            all_analyzed_event,
            9003,
            config["data_folder"],
            config["resultFolder"],
        )
    ),
    threading.Thread(
        target=analyze_loop_factory(
            files_queue,
            results_queue,
            all_analyzed_event,
            9004,
            config["data_folder"],
            config["resultFolder"],
        )
    ),
    threading.Thread(
        target=analyze_loop_factory(
            files_queue,
            results_queue,
            all_analyzed_event,
            9005,
            config["data_folder"],
            config["resultFolder"],
        )
    ),
    threading.Thread(
        target=analyze_loop_factory(
            files_queue,
            results_queue,
            all_analyzed_event,
            9006,
            config["data_folder"],
            config["resultFolder"],
        )
    ),
    threading.Thread(
        target=analyze_loop_factory(
            files_queue,
            results_queue,
            all_analyzed_event,
            9007,
            config["data_folder"],
            config["resultFolder"],
        )
    ),
    threading.Thread(
        target=analyze_loop_factory(
            files_queue,
            results_queue,
            all_analyzed_event,
            9008,
            config["data_folder"],
            config["resultFolder"],
        )
    ),
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
        test_run=config["testRun"],
        filename_parsing=config["filenameParsing"],
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

