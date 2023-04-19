import threading, queue
import argparse
from dotenv import load_dotenv
from worker.analyze import analyze_loop_factory
from worker.store import store_loop_factory
from util.db import init_db, DbWorker
from pytz import timezone
from create_reports import create_report

from util.tools import (
    load_config,
    load_files_list,
    load_json,
    load_files_list,
)
from util.db import drop_species_indices, create_species_indices
import os


def analyze(config_filepath, create_index=False,drop_index=False, create_report_flag=False, retry_corrupted_files=False):
    # print method paramaters

    if not os.path.exists("./cache"):
        os.makedirs("./cache")

    load_dotenv()  # load environment variables from .env
    print('Loading config from "{}"'.format(config_filepath))
    print("Create index: {}".format(create_index))
    config = load_config(config_filepath)
    analyze_thread_count = config["analyzeThreads"]
    print("ANALYZE_THREADS", analyze_thread_count)
    index_to_name = load_json(config["indexToNameFile"])
    if config["onlyAnalyze"] is False:
        init_db(config["prefix"], index_to_name)
    if create_index and config["onlyAnalyze"] is False or drop_index: 
        drop_species_indices(
            config["prefix"], species_index_list=config["speciesIndexList"],
        )
    for i in range(1, config["repeats"], 2):
        files_queue = queue.Queue()
        results_queue = queue.Queue()
        all_analyzed_event = threading.Event()

        # load_file_list
        worker = DbWorker(config["prefix"])
        processed_files = worker.get_all_filepaths()
        
        
        processed_count, files_count = load_files_list(config, files_queue,processed_files, retry_corrupted_files=retry_corrupted_files, prefix=config["prefix"])

        print(
            "Files found {} already processed {}".format(files_count, processed_count)
        )
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
                    model_output_style=config["modelOutputStyle"],
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
                only_analyze=config["onlyAnalyze"],
                retry_corrupted_files=retry_corrupted_files,
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

    if create_index and config["onlyAnalyze"] is False:
        create_species_indices(
            config["prefix"], species_index_list=config["speciesIndexList"],
        )
    if create_report_flag is True:
        create_report(prefix=config["prefix"], output_format="json")


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
    # parse argument for creating index default is False
    parser.add_argument(
        "--create_index", help="create index", action="store_true", default=False,
    )

    parser.add_argument(
        "--drop_index", help="drop index", action="store_true", default=False,
    )
    parser.add_argument(
        "--create_report", help="create json report", action="store_true", default=False
    )
    parser.add_argument(
        "--retry", help="retry corrupted files", action="store_true", default=False
    )

    args = parser.parse_args()
    if args.config_filepath:
        analyze(
            args.config_filepath,
            create_index=args.create_index,
            drop_index=args.drop_index,
            create_report_flag=args.create_report,
            retry_corrupted_files=args.retry,
        )
    else:
        print("No config file specified")
        exit(1)

