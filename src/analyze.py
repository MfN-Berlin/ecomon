from time import sleep
import requests
import requests
from os import path
import time


def analyze_loop_factory(
    files_queue,
    results_queue,
    all_analyzed_event,
    port,
    data_path,
    relative_result_path,
):
    def loop():
        while not files_queue.empty():

            filepath = files_queue.get()
            # print("analyze {}".format(filepath))
            # put raw filepath and analyze result filepath
            # "http://localhost:4001/identify?path=/mnt/file.wav&outputDir=/mnt/Results&outputStyle=resultDict"
            relative_file = path.relpath(filepath, start=data_path)
            result_path = path.join(
                data_path,
                relative_result_path,
                "{}.pkl".format((path.basename(filepath)).split(".")[0]),
            )

            request_string = "http://localhost:{port}/identify?path={filepath}&outputDir={result_path}&outputStyle=resultDict".format(
                port=port,
                filepath=path.join("/mnt/", relative_file),
                result_path=path.join("/mnt/", relative_result_path),
            )
            try:
                requests.get(request_string,)
                results_queue.put([filepath, result_path, None])
            except Exception as e:
                results_queue.put([filepath, None, e])

        # print("############ all analyzed ############")
        all_analyzed_event.set()

    return loop
