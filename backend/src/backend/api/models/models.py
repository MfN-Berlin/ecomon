from typing import List, Literal
from pydantic import BaseModel


class AnalyzeSiteRequest(BaseModel):
    site_id: int


class AnalyzeSiteResponse(BaseModel):
    job_id: int
