import argparse
import os
import glob


def main(
    configs,
    retry=False,
    create_report=False,
    drop_index=False,
    create_index=False,
    generate_events=False,
    generate_histograms=False,
    all=False,
):
    # Add YAML configs from folder to configs list
    for config in configs:
        paths = []
        if os.path.isdir(config):
            # Collect all YAML files in the directory
            for file_path in glob.glob(os.path.join(config, "*.yaml")):
                paths.append(file_path)
        else:
            paths.append(config)
    
        print("Importing the following configs: {}".format(paths))
        for path in paths:
            print("Importing: {}".format(path)  )
            cmd_str = "python3 import/import_records.py " + path

            if drop_index or all:
                cmd_str += " --drop_index"
            if retry:
                cmd_str += " --retry"
            if create_index or all:
                cmd_str += " --create_index"
            if create_report or all:
                cmd_str += " --create_report"
            if generate_events or all:
                cmd_str += " --generate_events"

            if generate_histograms or all:
                cmd_str += " --generate_histograms"

            os.system(cmd_str)



if __name__ == "__main__":
    # Parse command line arguments and run main
    # Parse a list of config files and a path to the config folder
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
        "--create_report", help="create JSON report", action="store_true", default=False
    )
    parser.add_argument(
        "--generate_events", help="generate events", action="store_true", default=False
    )
    parser.add_argument(
        "--generate_histograms", help="generate histograms", action="store_true", default=False
    )
    parser.add_argument(
        "--all", help="generate all (report, index, events, histograms)", action="store_true", default=False
    )
    args = parser.parse_args()
    configs = args.configs or []

    main(
        configs,
        retry=args.retry,
        create_index=args.create_index,
        drop_index=args.drop_index,
        create_report=args.create_report,
        generate_events=args.generate_events,
        generate_histograms=args.generate_histograms,
        all=args.all,
    )
