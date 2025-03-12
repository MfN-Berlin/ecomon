from pydantic import field_validator
import logging
from backend.shared.backend_base_settings import BackendBaseSettings


class WorkerSettings(BackendBaseSettings):
    redis_host: str
    redis_port: str
    audio_extensions: str = "wav,mp3,flac"
    wait_for_soft_cancel_timeout: int = 10

    @property
    def broker_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def backend_url(self) -> str:
        return self.broker_url

    @property
    def database_url(self) -> str:
        # For Celery, we need the sync database URL
        return (
            f"postgresql://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def audio_extensions_list(self) -> list[str]:
        # Convert comma-separated string to list of extensions
        return [f".{x.strip()}" for x in self.audio_extensions.split(",")]
