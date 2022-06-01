from time import sleep


def analyze_loop_factory(files_queue, results_queue, all_analyzed_event):
    def loop():
        while not files_queue.empty():
            filepath = files_queue.get()
            print("analyze {}".format(filepath))
            # put raw filepath and analyze result filepath
            results_queue.put([filepath, "s_{}".format(filepath)])
            sleep(0.5)
        print("############ all analyzed ############")
        all_analyzed_event.set()
    return loop
