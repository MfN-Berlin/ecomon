import argparse
import os
import glob


def main(
    configs,
    config_folder,
    retry=False,
    create_report=False,
    drop_index=False,
    create_index=False,
):
    # add YAML configs from folder to configs list
    if config_folder:
        for file_path in glob.glob(os.path.join(config_folder, "*.yaml")):
            configs.append(file_path)
        print("Found configs: ", configs)
    for config in configs:  #
        cmd_str = (
            "python3 import/import_records.py " + config + " --drop_index"
            if drop_index
            else "" + " --retry"
            if retry
            else "" + " --create_index"
            if create_index
            else "" + " --create_report"
            if (create_report)
            else ""
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
        "--drop_index", help="drop index", action="store_true", default=False,
    )

    parser.add_argument(
        "--create_index", help="create index", action="store_true", default=False,
    )
    parser.add_argument(
        "--retry", help="retry ", action="store_true", default=False,
    )
    parser.add_argument(
        "--create_report", help="create json report", action="store_true", default=False
    )
    args = parser.parse_args()
    configs = args.configs or []
    config_folder = args.config_folder
    main(
        configs,
        config_folder,
        retry=args.retry,
        create_index=args.create_index,
        drop_index=args.drop_index,
        create_report=args.create_report,
    )
