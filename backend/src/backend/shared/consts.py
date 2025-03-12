from enum import Enum


class TaskTopics(Enum):
    SCAN_DIRECTORIES = "scan_directories"
    CREATE_SITE_DATA_REPORT = "create_site_data_report"


# Usage
task_topic = TaskTopics.SCAN_DIRECTORIES
