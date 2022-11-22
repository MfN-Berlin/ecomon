from time import sleep
import threading, queue
import yaml
import glob
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


load_dotenv()  # load environment variables from .env
analyze_thread_count = int(os.getenv("BAI_ANALYZE_THREADS", 1))
print("ANALYZE_THREADS", analyze_thread_count)
# CONFIG_FILEPATH = "./backend/config/config-MBG01.yaml"
# CONFIG_FILEPATH = "./backend/config/config-BRITZ01.yaml"
# CONFIG_FILEPATH = "./backend/config/config.yaml"
# CONFIG_FILEPATH = "./backend/config/config-BRITZ02.yaml"
# CONFIG_FILEPATH = "./backend/config/config-BRITZ01-2019.yaml"
# CONFIG_FILEPATH = "./backend/config/config-BRITZ01-2020.yaml"
# CONFIG_FILEPATH = "./backend/config/config-BRITZ01-2021.yaml"
CONFIG_FILEPATH = "./backend/config/config-WALLBERGE-2022.yaml"
# CONFIG_FILEPATH = "./backend/config/config-WALLBERGE-2021.yaml"
# CONFIG_FILEPATH = "./backend/config/config-WALLBERGE-2020.yaml"
# CONFIG_FILEPATH = "./backend/config/config-WALLBERGE-2019.yaml"
# CONFIG_FILEPATH = "./backend/config/config-WALLBERGE-2018.yaml"
# CONFIG_FILEPATH = "./backend/config/config-CRIEWEN2022_01.yaml"
# CONFIG_FILEPATH = "./backend/config/config-CRIEWEN2022_05.yaml"

config = load_config(CONFIG_FILEPATH)

index_to_name = load_json(config["indexToNameFile"])

init_db(config["prefix"], index_to_name)


drop_species_indices(
    config["prefix"], species_index_list=config["speciesIndexList"],
)
for i in range(1, 10, 1):
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
                9000 + i,
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
            all_analyzed_event,
            results_queue,
            processed_count,
            files_count,
            config["error_cache_filepath"],
            test_run=config["testRun"],
            filename_parsing=config["filenameParsing"],
            species_index_list=config["speciesIndexList"],
            timezone=timezone(config["timezone"]) if config["timezone"] else None,
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

create_species_indices(
    config["prefix"], species_index_list=config["speciesIndexList"],
)
