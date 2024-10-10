import datetime

import json
import os
from datetime import datetime, timezone
from schemas.route_types import LastUpdate, Message, ResultJob
from sql.query import (
    delete_job,
    get_all_jobs as get_all_jobs_query,
    get_job_by_id,
    delete_job as delete_job_query,
    get_max_updated_at_from_jobs,
)
from fastapi import HTTPException,APIRouter
from typing import List, Optional, Union
from logging import getLogger
logger = getLogger(__name__)
from db import database
router = APIRouter()



@router.get(
    "/last_update", response_model=LastUpdate, operation_id="getLastUpdate"
)
async def get_last_update():
    job = await database.fetch_one(get_max_updated_at_from_jobs())
    if job and job[0]:
        # Ensure the datetime is timezone aware
        if job[0].tzinfo is None or job[0].tzinfo.utcoffset(job[0]) is None:
            job_date = job[0].replace(tzinfo=timezone.utc)
        else:
            job_date = job[0].astimezone(timezone.utc)

        iso_date = job_date.isoformat()
        return {"last_update": iso_date}
    else:
        # Handle case where no date is found or date is None
        return {"last_update": None}

@router.get("/", response_model=List[ResultJob], operation_id="getAllJobs")
async def get_all_jobs(
    prefix: Union[str, None] = None,
    type: Union[str, None] = None,
    status: Union[str, None] = None,
) -> List[ResultJob]:
    logger.debug(f"Fetching jobs with prefix={prefix}, type={type}, status={status}")
    jobs = await database.fetch_all(
        get_all_jobs_query(prefix=prefix, type=type, status=status)
    )
    logger.debug(f"Jobs fetched: {jobs}")
    result = []
    for job in jobs:
        result.append(
            {
                "id": job[0],
                "collection": job[1],
                "type": job[3],
                "status": job[2],
                "metadata": json.loads(job[4]),
                "progress": job[5],
                "error": job[6],
                "created_at": job[7],
                "updated_at": job[8],
            }
        )

    logger.debug(f"Result to return: {result}")
    return result

@router.get("/{id}", response_model=ResultJob, operation_id="getJobById")
async def get_job(id: int):
    job = await database.fetch_one(get_job_by_id(id))
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    else:
        return {
            "id": job[0],
            "collection": job[1],
            "type": job[3],
            "status": job[2],
            "metadata": json.loads(job[4]),
            "progress": job[5],
            "error": job[6],
            "created_at": job[7],
            "updated_at": job[8],
        }

@router.delete("/{id}", response_model=Message, operation_id="deleteJob")
async def delete_job(id: int):
    # get job and check in metadata for filepath
    job = await database.fetch_one(get_job_by_id(id))
    if job is None:
        return None
    else:
        # check if it is type create_sample
        if job[3] == "create_sample":
            # delete file
            result_directory = os.getenv("SAMPLE_FILES_DIRECTORY")
            metadata = json.loads(job[4])
            # logger.debug(metadata)
            result_directory = os.getenv("SAMPLE_FILES_DIRECTORY")
            result_filepath = os.path.join(result_directory, metadata["filename"])
            # logger.debug(result_filepath)
            if os.path.exists(result_filepath):
                os.remove(result_filepath)

        await database.execute(delete_job_query(id))
        return {"message": "job deleted"}
