
import threading, queue
import argparse
from dotenv import load_dotenv
from worker.analyze import analyze_loop_factory
from worker.store import store_loop_factory
from util.db import init_db
from pytz import timezone
from util.tools import (
    load_config,
    load_files_list,
    load_json,
    load_files_list,
)
from util.db import drop_species_indices, create_species_indices
import os



def analyze(config_filepath):
    load_dotenv()  # load environment variables from .env
    print('Loading config from "{}"'.format(config_filepath))
    config = load_config(config_filepath)
    analyze_thread_count = config["analyzeThreads"]
    print("ANALYZE_THREADS", analyze_thread_count)
    index_to_name = load_json(config["indexToNameFile"])
    init_db(config["prefix"], index_to_name)


    # drop_species_indices(
    #     config["prefix"], species_index_list=config["speciesIndexList"],
    # )
    for i in range(1, config["repeats"], 1):
        files_queue = queue.Queue()
        results_queue = queue.Queue()
        all_analyzed_event = threading.Event()

        # load_file_list
        processed_count, files_count = load_files_list(config, files_queue)

        print("Files found {} already processed {}".format(files_count, processed_count))
        # Created the Threads

        analyze_threads = [
            threading.Thread(
                target=analyze_loop_factory(
                    files_queue,
                    results_queue,
                    all_analyzed_event,
                    config["basePort"]
                    + (0 if config["allThreadsUseSamePort"] is True else i),
                    config["data_folder"],
                    config["resultFolder"],
                )
            )
            for i in range(analyze_thread_count)
        ]

        store_thread = threading.Thread(
            target=store_loop_factory(
                config["prefix"],
                config["progress_cache_filepath"],
                config["error_cache_filepath"],
                all_analyzed_event,
                results_queue,
                processed_count,
                files_count,
                test_run=config["testRun"],
                filename_parsing=config["filenameParsing"],
                timezone=timezone(config["timezone"]) if config["timezone"] else None,
                index_to_name=index_to_name if config["transformModelOutput"] else None,
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

        print("Join store_thread")
        store_thread.join()
        print("Done")

    # create_species_indices(
    #     config["prefix"], species_index_list=config["speciesIndexList"],
    # )

# parse parameter when called as script
if __name__ == "__main__":
    # parse config_filepath as first parameter is needed
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_filepath",
        help="path to config file",
        type=str,
        default=None,
        nargs="?",
    )
    args = parser.parse_args()
    if args.config_filepath:
        analyze(args.config_filepath)
    else:
        print("No config file specified")
        exit(1)




   
