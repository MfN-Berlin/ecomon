from time import sleep
import dotenv
import requests
import requests
from os import path, getenv
import time


def analyze_loop_factory(
    files_queue,
    results_queue,
    all_analyzed_event,
    port,
    data_path,
    relative_result_path,
    model_output_style=None,
):
    def loop():
        while not files_queue.empty():

            filepath = files_queue.get()
            # print("analyze {}".format(filepath))
            # put raw filepath and analyze result filepath
            # "http://localhost:4001/identify?path=/mnt/file.wav&outputDir=/mnt/Results&outputStyle=resultDict"
            relative_file = path.relpath(filepath, start=data_path)
            result_path = path.join(
                getenv("MDAS_RESULT_DIRECTORY"),
                relative_result_path,
                "{}.pkl".format((path.basename(filepath)).split(".")[0]),
            )
            # check if result file does not exists
            try:
                if not path.exists(result_path):
                    request_string = "http://localhost:{port}/identify?path={filepath}&outputDir={result_path}{model_output_style}".format(
                        port=port,
                        filepath=path.join("/mnt/data", relative_file),
                        result_path=path.join("/mnt/result", relative_result_path),
                        model_output_style="&outputStyle={}".format(model_output_style)
                        if model_output_style
                        else "",
                    )
                    requests.get(request_string,)
                # else:
                #     print("File {} already exists".format(result_path))
                results_queue.put([filepath, result_path, None, port])
            except Exception as e:
                results_queue.put([filepath, None, e, port])
            # results_queue.put([filepath, None, None])
        # print("############ all analyzed ############")
        all_analyzed_event.set()
       
    return loop
