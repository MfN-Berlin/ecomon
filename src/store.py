from time import sleep
from tqdm import tqdm


def store_loop_factory(
    processed_files_filepath,
    all_analyzed_event,
    results_queue,
    processed_count,
    files_count,
):
    def loop():
        with tqdm(
            total=files_count,
            initial=processed_count,
            desc="Analyzed",
            unit="files",
            smoothing=0.1,
        ) as progress:
            with open(processed_files_filepath, "a") as processed_f:
                while not results_queue.empty() or not all_analyzed_event.is_set():
                    if results_queue.empty():
                        sleep(1)
                        continue
                    filepath = results_queue.get()
                    # print("store {}".format(filepath[1]))
                    # write filepath to processed to file
                    processed_f.write(filepath[0] + "\n")
                    processed_f.flush()
                    progress.update(1)
                    sleep(0.1)

    return loop
