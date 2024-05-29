import os
import re
import argparse
from logging  import getLogger
logger = getLogger(__name__)
# regular expression for matching the old filename pattern
# old_filename_pattern = re.compile(r"^([A-Za-z0-9]+)_(\d{6})_(\d{6})\.wav$")
old_filename_pattern = re.compile(r"^([A-Za-z0-9]+)_(\d{6})_(\d{6})\.pkl$")
# FILE_ENDING = ".wav"
FILE_ENDING = ".pkl"
# parse command line arguments
parser = argparse.ArgumentParser(
    description="Rename .wav files in directory according to specified pattern"
)
parser.add_argument(
    "dir_path", help="path to directory containing .wav files to rename"
)
parser.add_argument(
    "--rename",
    action="store_true",
    help="rename files (default: test run without renaming files)",
)
args = parser.parse_args()

if not args.dir_path:
    parser.error("You must provide a directory path to rename .wav files.")

# recursively loop through all files in the directory and subdirectories
for dirpath, dirnames, filenames in os.walk(args.dir_path):
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)

        # check if the file is a .wav file and matches the old filename pattern
        if filename.endswith(FILE_ENDING) and old_filename_pattern.match(filename):
            # extract the old date components from the filename
            old_prefix, old_date, old_timestamp = old_filename_pattern.match(
                filename
            ).groups()
            old_date_str = f"{old_date}_{old_timestamp}"

            # create the new filename
            new_filename = f"{old_prefix}_20{old_date_str}{FILE_ENDING}"
            new_file_path = os.path.join(dirpath, new_filename)

            # logger.debug the rename command if in test mode
            if not args.rename:
                logger.debug(f"{filename} -> {new_filename}")
            # otherwise, rename the file
            else:
                os.rename(file_path, new_file_path)
