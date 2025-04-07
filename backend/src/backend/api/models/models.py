from datetime import datetime
from pydantic import BaseModel


class InferenceSiteRequest(BaseModel):
    site_id: int
    model_id: int
    start_datetime: datetime
    end_datetime: datetime


class JobActionResponse(BaseModel):
    job_id: int


class CreateVoucherRequest(BaseModel):
    site_id: int
    model_id: int
    label_ids: list[int]
    sample_count: int
    start_datetime: datetime
    end_datetime: datetime
    audio_padding_ms: int
    high_pass_filter_frequency_hz: int
