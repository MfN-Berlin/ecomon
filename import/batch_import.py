import argparse
import os


def main(configs):
    for config in configs:
        os.system("python3 import/import_records.py " + config + " --create_index")


if __name__ == "__main__":
    # parse command line arguments and run main
    # parse a list of config files
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "configs", help="list of config files", type=str, default=None, nargs="*",
    )
    args = parser.parse_args()
    if args.configs:
        main(args.configs)
    else:
        print("No config file specified")
        exit(1)

