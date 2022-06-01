from time import sleep
import threading, queue
import yaml
import glob
from dotenv import load_dotenv
from analyze import analyze_loop_factory
from store import store_loop_factory
from db import init_db

load_dotenv()  # load environment variables from .env

files_queue = queue.Queue()
results_queue = queue.Queue()

FILES_FOLDER = "/home/bewr/Dokumente/Audioaufnahmen/Britz02/"
PROCESSED_FILES = "processed_files.txt"

all_analyzed_event = threading.Event()


def load_files_list():
    print("load files list")
    lines = []

    files_count = 0
    with open(PROCESSED_FILES, "r") as processed_f:
        lines = processed_f.readlines()
    processed_dict = {}
    for filepath in lines:
        processed_dict[filepath] = True

    for filepath in glob.iglob(FILES_FOLDER + "**/*.wav", recursive=True):
        files_count += 1
        if processed_dict.get(filepath, False):
            # if file is allready processed do not add
            continue
        files_queue.put(filepath)
    return len(lines), files_count


init_db("test")
# load_file_list
processed_count, files_count = load_files_list()

# Created the Threads
analyze_thread = threading.Thread(
    target=analyze_loop_factory(files_queue, results_queue, all_analyzed_event,)
)
store_thread = threading.Thread(
    target=store_loop_factory(
        PROCESSED_FILES, all_analyzed_event, results_queue, processed_count, files_count
    )
)

# Started the threads
print("Start analyze_thread")
analyze_thread.start()
print("Start store_thread")
store_thread.start()


# Joined the threads
analyze_thread.join()
store_thread.join()

