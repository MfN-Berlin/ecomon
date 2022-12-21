from typing import NamedTuple
from datetime import date


FileNameInformation = NamedTuple(
    "FileNameInformation_name_date_time",
    [("location_name", str), ("record_datetime", date),],
)


def species_row_to_name(string):
    tmp = string[0].upper() + string[1:]
    tmp = tmp.replace("_", " ")
    return tmp
