from pydantic_settings import BaseSettings
from pydantic import field_validator
import logging


class BackendBaseSettings(BaseSettings):
    db_username: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    base_data_directory: str = "/data"
    log_level: str = "INFO"
    debug: bool = False

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> int:
        value = value.upper()
        if value not in logging._nameToLevel:  # type: ignore
            raise ValueError(
                f"Invalid log level: {value}. Valid options: DEBUG, INFO, WARNING, ERROR, CRITICAL"
            )
        return value

    class Config:
        env_file = ".env"
        extra = "ignore"
