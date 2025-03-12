from asyncio import sleep
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.services.directory_service import DirectoryService
from backend.api.models.directory import DirectoryInfo, SiteDirectoryChangeRequest
from backend.api.services.job_service import JobService
from backend.api.services.site_service import SiteService
from backend.api.settings import ApiSettings
from backend.worker.tasks.scan_directories_task import scan_directories_task
from backend.worker.tasks.delete_records_from_site_task import (
    delete_records_from_site_task,
)

from backend.api.database import get_db
from celery.result import AsyncResult
from backend.shared.consts import task_topic

router = APIRouter(prefix="/sites", tags=["sites"])
directory_service = DirectoryService(ApiSettings())


@router.post("/directory-changed")
async def directory_changed(
    payload: SiteDirectoryChangeRequest, db: AsyncSession = Depends(get_db)
):
    site_service = SiteService(db)
    job_service = JobService(db)

    if payload.operation == "INSERT":

        # check if all directories are part of a site
        if not await site_service.are_all_directories_part_of_site(
            payload.site_id, [payload.directory]
        ):
            raise HTTPException(
                status_code=400, detail="Directory not part of the site"
            )

        # Create a job in database, get a unique job_id
        job_id = await job_service.create_job(
            f"{task_topic.SCAN_DIRECTORIES.value}",
            payload={
                "site_id": payload.site_id,
                "directories": [payload.directory],
            },
        )

        celery_task_id = str(job_id)

        task = scan_directories_task.apply_async(
            task_id=celery_task_id + "",  # so Celery task_id and DB job_id match
            kwargs={"site_id": payload.site_id, "directories": [payload.directory]},
        )

        return {"job_id": job_id, "celery_task_id": task.id}

    if payload.operation == "DELETE":
        # delete the job from the database
        job_id = await job_service.create_job(
            "delete_records_from_site",
            payload={"site_id": payload.site_id, "directories": [payload.directory]},
        )

        celery_task_id = str(job_id)

        task = delete_records_from_site_task.apply_async(
            task_id=celery_task_id,  # so Celery task_id and DB job_id match
            kwargs={"site_id": payload.site_id, "directories": [payload.directory]},
        )

        return {"job_id": job_id, "celery_task_id": task.id}


@router.post("/scan-directories")
async def scan_directories():
    return {"job_id": 1}


@router.get(
    "/list-data-directories",
    response_model=List[DirectoryInfo],
    summary="List directories in data folder",
    description="Lists all folders in the data directory. Optional subpath parameter to list specific subdirectory.",
)
async def list_data_directories(
    subpath: Optional[str] = None,
) -> List[DirectoryInfo]:
    response = await directory_service.list_directories(subpath)
    return response


@router.post("/jobs/")
async def create_job(
    job_topic: str, payload: Optional[dict] = None, db: AsyncSession = Depends(get_db)
):
    job_service = JobService(db)
    job_id = await job_service.create_job(job_topic, payload)
    return {"job_id": job_id}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job_service = JobService(db)
    return await job_service.get_job_status(job_id)
