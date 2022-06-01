from time import sleep
import threading, queue
from isort import file
import yaml
from datetime import timedelta, datetime
from os import path
import glob
from store import store_loop_factory
from analyze import analyze_loop_factory

files_queue = queue.Queue()
results_queue = queue.Queue()

FILES_FOLDER = "/home/bewr/Dokumente/Audioaufnahmen/Britz02/"
PROCESSED_FILES = "processed_files.txt"

all_analyzed_event = threading.Event()


def load_files_list():
    print("load files list")
    lines = []
    with open(PROCESSED_FILES, "r") as processed_f:
        lines = processed_f.readlines()
    processed_dict = {}
    for filepath in lines:
        processed_dict[filepath] = True

    for filepath in glob.iglob(FILES_FOLDER + "**/*.wav", recursive=True):
        if processed_dict.get(filepath, False):
            # if file is allready processed do not add
            continue
        files_queue.put(filepath)


def analyze_loop():
    while not files_queue.empty():
        filepath = files_queue.get()
        print("analyze {}".format(filepath))
        # put raw filepath and analyze result filepath
        results_queue.put([filepath, "s_{}".format(filepath)])
        sleep(0.5)
    print("############ all analyzed ############")
    all_analyzed_event.set()


# Created the Threads
analyze_thread = threading.Thread(
    target=analyze_loop_factory(files_queue, results_queue, all_analyzed_event)
)
store_thread = threading.Thread(
    target=store_loop_factory(PROCESSED_FILES, all_analyzed_event, results_queue)
)
# load_file_list
load_files_list()

# Started the threads
print("Start analyze_thread")
analyze_thread.start()
print("Start store_thread")
store_thread.start()


# Joined the threads
analyze_thread.join()
store_thread.join()

