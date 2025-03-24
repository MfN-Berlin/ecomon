# record_errors as enum
from enum import Enum
from dataclasses import dataclass


class RecordErrorsEnum(Enum):
    FILE_READ_ERROR = "file_read_error"
    MISSING_FILE_PREFIX = "missing_file_prefix"
    RECORD_DATETIME_FORMAT = "record_datetime_format"
    DURATION_MISSMATCH = "duration_missmatch"
    SAMPLERATE_MISSMATCH = "samplerate_missmatch"


@dataclass
class RecordError:
    type: RecordErrorsEnum
    message: str
