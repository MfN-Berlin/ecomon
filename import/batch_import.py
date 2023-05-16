import argparse
import os
import glob


def main(
    configs,

    retry=False,
    create_report=False,
    drop_index=False,
    create_index=False,
):
    # add YAML configs from folder to configs list

    for config in configs:  #
        pathes = []
        if os.path.isdir(config):
            for file_path in glob.glob(os.path.join(config, "*.yaml")):
                pathes.append(file_path)
        else: 
            pathes.append(config)
        for path in pathes: 
            cmd_str = (
                "python3 import/import_records.py " + path + " --drop_index"
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

    main(
        configs,
        
        retry=args.retry,
        create_index=args.create_index,
        drop_index=args.drop_index,
        create_report=args.create_report,
    )
