from typing import NamedTuple
from datetime import date
import os
import shutil
import zipfile

FileNameInformation = NamedTuple(
    "FileNameInformation_name_date_time",
    [
        ("location_name", str),
        ("record_datetime", date),
    ],
)


def species_row_to_name(string):
    tmp = string[0].upper() + string[1:]
    tmp = tmp.replace("_", " ")
    return tmp


def pad_int_with_zeros(num, digits):
    return str(num).zfill(digits)


def first_letter_to_upper_case(string):
    return string[0].upper() + string[1:]


def zip_folder_and_delete(folder_path, output_filepath):
    zip_file = zipfile.ZipFile(output_filepath, "w")
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            zip_file.write(os.path.join(root, file), file)
    zip_file.close()
    shutil.rmtree(folder_path)


# transform milliseconds to hh:mm:ss format
def s_to_time(s):
    cent_seconds = round(((s + 0.2) % 1) * 100)
    seconds = s
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    result = "%02d%02d%02d%02d" % (hours, minutes, seconds, cent_seconds)

    return result
