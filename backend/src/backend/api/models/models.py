from datetime import datetime
from pydantic import BaseModel


class AnalyzeSiteRequest(BaseModel):
    site_id: int
    model_id: int
    start_datetime: datetime
    end_datetime: datetime


class AnalyzeSiteResponse(BaseModel):
    job_id: int
