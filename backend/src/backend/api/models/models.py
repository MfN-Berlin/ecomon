from datetime import datetime
from pydantic import BaseModel


class InferenceSiteRequest(BaseModel):
    site_id: int
    model_id: int
    start_datetime: datetime
    end_datetime: datetime


class InferenceSiteResponse(BaseModel):
    job_id: int
