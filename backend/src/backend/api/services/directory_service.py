import asyncio
import logging
from logging.config import dictConfig
from pathlib import Path
from typing import List, Optional
from fastapi import HTTPException
from dotenv import load_dotenv
from backend.api import settings
from backend.api.models.directory import DirectoryInfo
from backend.api.settings import ApiSettings
from backend.api.logger_config import get_log_config


dictConfig(get_log_config(timestamp=True))
logger = logging.getLogger(__name__)


class DirectoryService:
    def __init__(self, settings: ApiSettings):
        load_dotenv()
        base_dir = Path(settings.base_data_directory)
        if not base_dir.exists():
            raise HTTPException(
                status_code=500, detail=f"Base directory '{base_dir}' does not exist"
            )

        self.base_dir = base_dir

    def _validate_target_path(self, subpath: Optional[str]) -> Path:
        logger.debug(f"Validating target path with subpath: {subpath}")
        target_path = self.base_dir
        if subpath:
            try:
                target_path = (self.base_dir / subpath).resolve()
                if not str(target_path).startswith(str(self.base_dir.resolve())):
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid path: Cannot access directories outside base path",
                    )
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid path format")

        if not target_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Directory '{subpath if subpath else ''}' not found",
            )
        logger.debug(f"Target path: {target_path}")
        return target_path

    async def _get_directories(self, path: Path) -> list:
        directories = []
        try:
            # Use asyncio to run the blocking I/O operation in a separate thread
            items = await asyncio.to_thread(lambda: list(path.iterdir()))
            for item in items:
                if item.is_dir():
                    dir_info = DirectoryInfo(
                        name=item.name, path=str(item.relative_to(self.base_dir))
                    )
                    directories.append(dir_info)
        except PermissionError:
            raise HTTPException(
                status_code=403, detail=f"Permission denied accessing {path}"
            )

        return directories

    async def list_directories(
        self, subpath: Optional[str] = None
    ) -> List[DirectoryInfo]:
        logger.debug(f"Listing directories with subpath: {subpath}")
        # Run synchronous validation
        target_path = self._validate_target_path(subpath)
        # Get directories asynchronously
        directories = await self._get_directories(target_path)
        # Create and return the response object

        return directories
