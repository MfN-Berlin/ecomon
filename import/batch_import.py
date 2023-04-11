import argparse
import os
import glob


def main(configs, config_folder, no_index=False):
    # add YAML configs from folder to configs list
    if config_folder:
        for file_path in glob.glob(os.path.join(config_folder, "*.yaml")):
            configs.append(file_path)
        print("Found configs: ", configs)
    for config in configs:  #
        cmd_str = (
            "python3 import/import_records.py "
            + config
            + (" --only_drop_index" if no_index else " --create_index")
            + " --create_report"
        )
        print(cmd_str)
        os.system(cmd_str)


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
    parser.add_argument(
        "--no_index",
        help="path to folder containing YAML config files",
        action="store_true",
    )
    args = parser.parse_args()
    configs = args.configs or []
    config_folder = args.config_folder
    main(configs, config_folder)
