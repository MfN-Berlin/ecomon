from dotenv import load_dotenv
from util.db import DbWorker
import argparse
import os
import glob
import yaml


def main(paths):
    # Process YAML configs from folders or files
    load_dotenv()
    for path in paths:
        yaml_files = []
        if os.path.isdir(path):
            # Collect all YAML files in the directory
            for file_path in glob.glob(os.path.join(path, "*.yaml")):
                yaml_files.append(file_path)
        elif os.path.isfile(path) and path.endswith(".yaml"):
            yaml_files.append(path)
        else:
            print(f"'{path}' is not a recognized directory or YAML file. Skipping...")
            continue

        print(f"Creating index for configs: {yaml_files}")

        for yaml_file in yaml_files:
            # read config yaml file

            with open(yaml_file, "r") as stream:
                try:
                    config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
            collection = config.get("prefix")
            print(f"Add indices to {collection}_predictions")
            db_worker = DbWorker(config.get("collection"))
            for species in config.get("speciesIndexList"):
                print(f"Adding index to {species}")
                try:
                    db_worker.add_index(collection, species)

                except Exception as e:
                    print(e)
                    db_worker.rollback()


if __name__ == "__main__":
    # Parse command line arguments and run main
    # Parse a list of folders and/or files
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "paths",
        help="list of folders and/or YAML config files",
        type=str,
        nargs="*",
    )

    args = parser.parse_args()
    main(args.paths)
