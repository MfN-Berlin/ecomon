from enum import Enum


class TaskTopics(Enum):
    SCAN_DIRECTORIES = "scan_directories"
    CREATE_SITE_DATA_REPORT = "create_site_data_report"
    MODEL_INFERENCE_SITE = "model_inference_site"
    CREATE_VOUCHER = "create_voucher"
    CHECK_SITE_RECORD_ERRORS = "check_site_record_errors"


# Usage
task_topic = TaskTopics.SCAN_DIRECTORIES
