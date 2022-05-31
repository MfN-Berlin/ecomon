from time import sleep
import threading, queue
import yaml
from datetime import timedelta, datetime
from os import path
import glob

files_queue = queue.Queue()
results_queue = queue.Queue()

FILES_FOLDER = "/home/bewr/Dokumente/Britz02/"
PROCESSED_FILES = "/home/bewr/projects/mfn/batch-audiofile-inferencing/processed_files.txt"

all_analyzed_event = threading.Event()
def load_files_list():
    print("load files list")
    with open(PROCESSED_FILES,"a") as processed_f:
        processed_f.readlines()
    for filename in glob.iglob(FILES_FOLDER + '**/*.wav', recursive=True):
        files_queue.put(filename)

def analyze_loop():
    while not files_queue.empty():
        filepath = files_queue.get()
        print("analyze {}".format(filepath))
        # put raw filepath and analyze result filepath
        results_queue.put([filepath, "s_{}".format(filepath)])
        sleep(0.5)
    print("##############all analyzed ############")
    all_analyzed_event.set()
def store_loop():
    with open(PROCESSED_FILES,"a") as processed_f:
        while not results_queue.empty() or not all_analyzed_event.is_set():
            if(results_queue.empty()):
                sleep(1)
                continue
            filepath = results_queue.get()
            processed_f.write(filepath[0]+'\n')
            processed_f.flush()
            sleep(0.5)




# Created the Threads
analyze_thread = threading.Thread(target=analyze_loop)
store_thread = threading.Thread(target=store_loop)
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

