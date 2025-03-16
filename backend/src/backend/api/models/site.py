from typing import List, Literal
from pydantic import BaseModel


class CreateDataReportRequest(BaseModel):
    site_id: int


class CreateDataReportResponse(BaseModel):
    job_id: int


class SiteDirectoryChangeRequest(BaseModel):
    site_id: int
    directory: str
    operation: Literal["INSERT", "DELETE"]


class SiteDirectoriesScanRequest(BaseModel):
    site_id: int


class SiteDirectoriesScanResponse(BaseModel):
    job_id: int


class SiteDataReportResponse(BaseModel):
    job_id: int


class SiteDirectoryScanRequest(BaseModel):
    site_id: int
    directory: str


class SiteDirectoryScanResponse(BaseModel):
    job_id: int
