from typing import List, Literal
from pydantic import BaseModel


class DirectoryInfo(BaseModel):
    name: str
    path: str


class SiteDirectoryChangeRequest(BaseModel):
    site_id: int
    directory: str
    operation: Literal["INSERT", "DELETE"]


class SiteDirectoryScanRequest(BaseModel):
    site_id: int
    directories: List[str]
