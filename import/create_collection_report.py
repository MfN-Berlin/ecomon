import json
from dotenv import load_dotenv
import os
import argparse
from util.tools import (
    load_config,
    load_files_list,
)

def main(config_filepath):
    if not os.path.exists("./reports"):
        os.makedirs("./reports")

    load_dotenv()  # load environment variables from .env

   
    if os.path.isfile(config_filepath):
        configs = [config_filepath]
    else:
        # get all yaml files in folder config_filepath
        configs = [os.path.join(config_filepath, f) for f in os.listdir(config_filepath) if f.endswith('.yaml')]

    for config_file in configs:
        config = load_config(config_file)
        folders = config["recordFolder"]
        # count wav files in folders and make a historgram of filesizes
        files=[]
        load_files_list(config, files)
        size_histogram = {}
        for file in files:
            #get size of file in mb and round to nearest 10
            size = round(os.path.getsize(file)/1000000, -1)
            if size in size_histogram:
                size_histogram[size] += 1
            else:
                size_histogram[size] = 1
        # caluclate toal size of files in mb
        total_size = 0
        for size in size_histogram:
            total_size += size_histogram[size]*size


        result = {
            "size_histogram": size_histogram,
            "total_files": len(files),
            "total_size": total_size,
        }
        filename = config["prefix"]+"-collection-report.json"
        with open("./reports/"+filename, "w") as f:
            json.dump(result, f, indent=2)


   
    
    


# parse parameter when called as script
if __name__ == "__main__":
    # parse config_filepath as first parameter is needed
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_filepath",
        help="path to config file",
        type=str,
        default=None,
        nargs="?",
    )
    # parse argument for creating index default is False
    parser.add_argument(
        "--create_index", help="create index", action="store_true", default=False,
    )

    args = parser.parse_args()
    if args.config_filepath:
        main(args.config_filepath)
    else:
        print("No config file specified")
        exit(1)