import asyncio
import time
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from os import path
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import FileResponse
from routes.prefix.predictions import JobId, do_add_index_job
from sql.query import add_job, update_job_status, get_job_by_id

from tasks.create_sample import create_sample
from fastapi import APIRouter
from db import database
from logging  import getLogger
logger = getLogger(__name__)
router = APIRouter()

class Record(BaseModel):
    id: int
    filepath: str
    filename: str
    record_datetime: datetime
    duration: float
    channels: int


class RandomSampleRequest(BaseModel):
    prefix: str
    species: str
    sample_size: Optional[int] = 10
    threshold_min: float
    threshold_max: float
    audio_padding: Optional[int] = 5
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    random: Optional[bool] = False
    high_pass_frequency: Optional[int] = 0
    zip_hours_off_set: Optional[int] = 0  # add timezone delta to  export zip filename


random_sample_executor = ThreadPoolExecutor(10)



# route to get random sample from prediction table
@router.post("/sample", response_model=JobId, operation_id="getRandomSample")
async def get_random_sample(request: RandomSampleRequest):
    # synchronous function in thread for asyncio compatibility
    TMP_DIRECTORY = os.getenv("TMP_DIRECTORY")
    if not path.exists(TMP_DIRECTORY):
        os.makedirs(TMP_DIRECTORY)
    # parse start string to datetime object

    if request.start_datetime:
        start_datetime = datetime.fromisoformat(
            request.start_datetime[:-1] + "+00:00"
        )

    else:
        start_datetime = None
    # parse end string to datetime object
    logger.debug(request.end_datetime)
    if request.end_datetime:
        end_datetime = datetime.fromisoformat(request.end_datetime[:-1] + "+00:00")
    else:
        end_datetime = None
    logger.debug(end_datetime)
    # logger.debug datetime to format YYYYMMSS_HHMMSS

    start_datetime_str = (
        start_datetime + timedelta(hours=request.zip_hours_off_set)
    ).strftime("%Y%m%d_%H%M%S")
    end_datetime_str = (
        end_datetime + timedelta(hours=request.zip_hours_off_set)
    ).strftime("%Y%m%d_%H%M%S")
    logger.debug(end_datetime_str)

    result_directory = os.getenv("SAMPLE_FILES_DIRECTORY")
    if not path.exists(result_directory):
        os.makedirs(result_directory)
    result_filename = "{time}_{prefix}_{species}_{threshold_min}_{threshold_max}_from_{from_date}_until_{until}_samples_{samples}_padding_{padding}.zip".format(
        time=round(time.time() * 1000),
        prefix=request.prefix,
        species=request.species,
        threshold_min="lq_{}_".format(request.threshold_min)
        if request.threshold_min != None or request.threshold_min == 0
        else "",
        threshold_max="hq_{}_".format(request.threshold_max)
        if request.threshold_max != None or request.threshold_max == 0
        else "",
        from_date=start_datetime_str,
        until=end_datetime_str,
        samples=request.sample_size,
        padding=request.audio_padding,
    )
    result_filepath = os.path.join(
        result_directory,
        result_filename,
    )

    async def task(database, job_id):
        loop = asyncio.get_event_loop()

        def func():
            create_sample(
                prefix=request.prefix,
                result_filepath=result_filepath,
                TMP_DIRECTORY=TMP_DIRECTORY,
                species=request.species,
                threshold_min=request.threshold_min,
                threshold_max=request.threshold_max,
                sample_size=request.sample_size,
                audio_padding=request.audio_padding,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                job_id=job_id,
                random=request.random,
                high_pass_frequency=request.high_pass_frequency,
            )

        await database.execute(update_job_status(job_id, "running"))

        await loop.run_in_executor(random_sample_executor, func)
        await database.execute(update_job_status(job_id, "done"))

    job_id = await database.execute(
        add_job(
            request.prefix,
            "create_sample",
            "pending",
            {
                "filename": result_filename,
                "filepath": result_filepath,
                "prefix": request.prefix,
                "species": request.species,
                "threshold_min": request.threshold_min,
                "threshold_max": request.threshold_max,
                "from": request.start_datetime,
                "until": request.end_datetime,
                "random": request.random,
                "samples": None if request.random else request.sample_size,
                "padding": request.audio_padding,
                "high_pass_frequency": request.high_pass_frequency,
            },
        )
    )
    logger.debug(f"Job {job_id} added to queue")
    asyncio.ensure_future(task(database, job_id))
    return {"job_id": job_id}
    # return file stream

    # return FileResponse(
    #     result_filepath, media_type="application/zip", filename=result_filename
    # )

@router.get("/random_sample/file/{filename}", operation_id="getRandomSampleFile")
async def get_random_sample(filename: str) -> FileResponse:
    result_directory = os.getenv("SAMPLE_FILES_DIRECTORY")
    result_filepath = os.path.join(result_directory, filename)
    return FileResponse(result_filepath, media_type="application/zip")
