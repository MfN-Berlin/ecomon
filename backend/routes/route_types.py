import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Literal


class QueryRequest(BaseModel):
    species: str
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None


class QueryResponse(BaseModel):
    predictions_count: int
    species_count: int


class JobId(BaseModel):
    job_id: int = None


class PredictionMax(BaseModel):
    record_id: int
    record_datetime: datetime.datetime
    value: float


class Collection(BaseModel):
    name: str
    species_list: List[str]
    records_count: int
    predictions_count: int
    indicated_species_columns: List[str]


class Species(BaseModel):
    name: str
    has_index: bool


class Duration(BaseModel):
    duration: int
    record_count: int


class Prediction(BaseModel):
    prediction_count: int
    record_count: int


class Summary(BaseModel):
    date: str
    count: int
    duration: float


class Report(BaseModel):
    first_record_datetime: str
    last_record_datetime: str
    records_count: int
    corrupted_record_count: int
    summed_records_duration: float
    predictions_count: int
    record_duration_histogram_query: List[Duration]
    record_prediction_count_histogram_query: List[Prediction]
    monthly_summary_query: List[Summary]
    daily_summary_query: List[Summary]


class EventResponse(BaseModel):
    predictions_count: int
    species_count: int


class BinSizeRequest(BaseModel):
    collection_name: str
    start_datetime: str
    end_datetime: str
    species: Optional[str] = None
    bin_width: Optional[float] = 0.02
    audio_padding: Optional[int] = 5


class PredictionsRequest(BaseModel):
    collection_name: str
    start_datetime: str
    end_datetime: str
    species: str
    audio_padding: Optional[int] = 5
    request_timezone: Optional[str] = "UTC"
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None


class VoucherRequest(BaseModel):
    collection_name: str
    species_list: List[str]
    sample_size: int
    audio_padding: Optional[int] = 5
    high_pass_frequency: Optional[int] = 0


class DailyHistogramRequest(BaseModel):
    collection_name: str
    start_datetime: str
    end_datetime: str
    species: str
    bin_width: Optional[float] = 0.02
    audio_padding: Optional[int] = 5
    request_timezone: Optional[str] = "UTC"
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None


class JobCreatedResponse(BaseModel):
    job_id: int


# define class of job
JobStatus = Literal["running", "done", "failed", "pending"]
JobTypes = Literal[
    "calc_bin_sizes",
    "calc_predictions",
    "calc_daily_histograms",
    "create_voucher",
    "add_index",
    "create_sample",
]


class Job(BaseModel):
    id: int
    collection: str
    job_type: JobTypes
    job_status: JobStatus
    metadata: str


class ResultJob(BaseModel):
    id: int
    collection: str
    type: JobTypes
    status: JobStatus
    metadata: Optional[dict] = None
    progress: str
    error: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class Message(BaseModel):
    message: str


class LastUpdate(BaseModel):
    last_update: datetime.datetime
