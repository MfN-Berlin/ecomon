from time import sleep
import requests
import requests
from os import path


def analyze_loop_factory(
    files_queue, results_queue, all_analyzed_event, port, data_path, relative_resultpath
):
    def loop():
        while not files_queue.empty():
            filepath = files_queue.get()
            # print("analyze {}".format(filepath))
            # put raw filepath and analyze result filepath
            # "http://localhost:4001/identify?path=/mnt/file.wav&outputDir=/mnt/Results&outputStyle=resultDict"
            relative_file = path.relpath(filepath, start=data_path)
            resultpath = path.join(
                data_path,
                relative_resultpath,
                "{}.pkl".format((path.basename(filepath)).split(".")[0]),
            )

            requeststring = "http://localhost:{port}/identify?path={filepath}&outputDir={resultpath}&outputStyle=resultDict".format(
                port=port,
                filepath=path.join("/mnt/", relative_file),
                resultpath=path.join("/mnt/", relative_resultpath),
            )
            requests.get(requeststring)

            results_queue.put([filepath, resultpath])

        # print("############ all analyzed ############")
        all_analyzed_event.set()

    return loop
