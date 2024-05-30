from time import sleep
import dotenv
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
    batchSize=None,
    nCpuWorkers=None,
    index_to_name=None,
    debug=False,
):
    if(debug):
        #print all parameters
        print(f'Analyze: files_queue: {files_queue}')
        print(f'Analyze: results_queue: {results_queue}')
        print(f'Analyze: all_analyzed_event: {all_analyzed_event}')
        print(f'Analyze: port: {port}')
        print(f'Analyze: data_path: {data_path}')
        print(f'Analyze: relative_result_path: {relative_result_path}')
        print(f'Analyze: model_output_style: {model_output_style}')
        print(f'Analyze: batchSize: {batchSize}')
        print(f'Analyze: nCpuWorkers: {nCpuWorkers}')
        print(f'Analyze: debug: {debug}')


    def loop():
        # print(f"Start Thread on requests on Port${port}")
        if(debug):
               print(f'Analyze: file_queue is empty {files_queue.empty()}')
        while not files_queue.empty():

            filepath = files_queue.get()
            if(debug):
                print(f"analyze: file {filepath}")
            # put raw filepath and analyze result filepath
            # "http://localhost:4001/identify?path=/mnt/file.wav&outputDir=/mnt/Results&outputStyle=resultDict"
            relative_file = path.relpath(filepath, start=data_path)
            result_path = path.join(
                getenv("RESULT_DIRECTORY"),
                relative_result_path,
                f"{(path.basename(filepath)).split('.')[0]}.pkl",
            )
            # check if result file does not exists
           
            try:
                if not path.exists(result_path):
                    container_filepath=path.join("/mnt/data", relative_file)
                    container_resultpath=path.join("/mnt/result", relative_result_path) 
                    request_string = f'http://localhost:{port}/identify?path={container_filepath}&outputDir={container_resultpath}&mono=True'
                    if(debug):
                        print(f'Analyze: container_filepath {container_filepath}')
                        print(f'Analyze: result_path {result_path}')
                    if(model_output_style):
                        request_string += f'&outputStyle={model_output_style}'
                    if(batchSize):
                        request_string += f'&batchSize={batchSize}'
                    if(nCpuWorkers):
                        request_string += f'&nCpuWorkers={nCpuWorkers}'

                    if(debug):
                        print(f'Analyze: Request string {request_string}')

                    requests.get(request_string)               
             
                sleep(0.1) #safty sleep
                results_queue.put([filepath, result_path, None, port])
                
            except Exception as e:
                if(debug):
                    print(f'Analyze Thread: error during request on port: {port}: {str(e)}')
                results_queue.put([filepath, None, e, port])
       
        all_analyzed_event.set()
       
    return loop
