from time import sleep


def store_loop_factory(processed_files_filepath, all_analyzed_event, results_queue):
    def loop():
        with open(processed_files_filepath, "a") as processed_f:
            while not results_queue.empty() or not all_analyzed_event.is_set():
                if results_queue.empty():
                    sleep(1)
                    continue
                filepath = results_queue.get()
                print("store {}".format(filepath[1]))
                # write filepath to processed to file
                processed_f.write(filepath[0] + "\n")
                processed_f.flush()
                sleep(0.1)

    return loop
