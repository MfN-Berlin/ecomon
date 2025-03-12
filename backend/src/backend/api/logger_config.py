import logging

from typing import Dict, Any
from backend.api.settings import ApiSettings

settings = ApiSettings()


class ColoredFormatter(logging.Formatter):
    # Define color codes
    COLORS = {
        "INFO": "\033[92m",  # Green
        "DEBUG": "\033[94m",  # Blue
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        # Temporarily store the original levelname
        original_levelname = record.levelname

        # Apply color only to the levelname
        level_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{level_color}{record.levelname}{self.RESET}"

        # Format the log record
        formatted_record = super().format(record)

        # Restore the original levelname so other handlers are not affected
        record.levelname = original_levelname

        return formatted_record


def get_log_config(timestamp: bool = False) -> Dict[str, Any]:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": (
                    "%(levelname)s:\t%(asctime)s - %(name)s - %(message)s"
                    if timestamp
                    else "%(levelname)s:\t%(name)s - %(message)s"
                ),
                "()": ColoredFormatter,
            },
        },
        "handlers": {
            "default": {
                "level": settings.log_level,
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "httpx": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "transformer_based_model": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "level": settings.log_level,
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
        },
    }

    return logging_config
