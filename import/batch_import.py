import argparse
import os
import glob


def main(configs, config_folder):
    # add YAML configs from folder to configs list
    if config_folder:
        for file_path in glob.glob(os.path.join(config_folder, "*.yaml")):
            configs.append(file_path)
        print("Found configs: ", configs)
    for config in configs:
        os.system(
            "python3 import/import_records.py "
            + config
            + " --create_index"
            + " --create_report"
        )


if __name__ == "__main__":
    # parse command line arguments and run main
    # parse a list of config files and a path to config folder
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "configs", help="list of config files", type=str, default=None, nargs="*",
    )
    parser.add_argument(
        "--config_folder",
        help="path to folder containing YAML config files",
        type=str,
        default=None,
    )
    args = parser.parse_args()
    configs = args.configs or []
    config_folder = args.config_folder
    main(configs, config_folder)
