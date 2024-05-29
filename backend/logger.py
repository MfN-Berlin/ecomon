import logging
import os
from logging.config import dictConfig

class ColoredFormatter(logging.Formatter):
    # Define color codes
    COLORS = {
        'INFO': '\033[92m',  # Green
        'DEBUG': '\033[94m',   # Blue
        'WARNING': '\033[93m',# Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m' # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        log_message = super().format(record)
        return f"{log_color}{log_message}{self.RESET}"

def get_log_config(log_level):
    _log_level = log_level.upper()
    logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(levelname)s\t%(asctime)s - %(name)s - %(message)s",
                    "()": "logger.ColoredFormatter"
                },
            },
            "handlers": {
                "default": {
                    "level": _log_level,
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "": {  # root logger
                    "handlers": ["default"],
                    "level": _log_level,
                    "propagate": True,
                },
                "uvicorn": {
                    "handlers": ["default"],
                    "level": _log_level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": _log_level,
                    "handlers": ["default"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": _log_level,
                    "propagate": False,
                },
            },
        }

    dictConfig(logging_config)