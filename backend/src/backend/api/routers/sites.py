from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.services.directory_service import DirectoryService
from backend.api.models.directory import DirectoryInfo
from backend.api.models.site import (
    CreateDataReportRequest,
    SiteDirectoryChangeRequest,
    SiteDirectoriesScanRequest,
    SiteDirectoriesScanResponse,
    SiteDataReportResponse,
    SiteDirectoryScanRequest,
    SiteDirectoryScanResponse,
)
from backend.api.services.job_service import JobService
from backend.api.services.site_service import SiteService
from backend.api.settings import ApiSettings
from backend.worker.tasks.create_site_data_report_task import (
    create_site_data_report_task,
)
from backend.worker.tasks.scan_directories_task import scan_directories_task
from backend.worker.tasks.delete_records_from_site_task import (
    delete_records_from_site_task,
)

from backend.api.database import get_db
from celery.result import AsyncResult
from backend.shared.consts import task_topic

router = APIRouter(prefix="/sites", tags=["sites"])
directory_service = DirectoryService(ApiSettings())

###
# Helper functions
###


async def check_directories_and_create_import_job(
    db: AsyncSession, site_id: int, directories: List[str]
):

    if not await SiteService(db).are_all_directories_part_of_site(site_id, directories):
        raise HTTPException(status_code=400, detail="Directory not part of the site")

    job_id = await JobService(db).create_job(
        f"{task_topic.SCAN_DIRECTORIES.value}",
        payload={
            "site_id": site_id,
            "directories": directories,
        },
    )

    celery_task_id = str(job_id)

    scan_directories_task.apply_async(
        task_id=celery_task_id + "",  # so Celery task_id and DB job_id match
        kwargs={"site_id": site_id, "directories": directories},
    )

    return job_id


###
# Endpoints
###


@router.post("/directory-changed")
async def directory_changed(
    payload: SiteDirectoryChangeRequest, db: AsyncSession = Depends(get_db)
):

    if payload.operation == "INSERT":
        job_id = await check_directories_and_create_import_job(
            db, payload.site_id, [payload.directory]
        )
        return {"job_id": job_id}

    if payload.operation == "DELETE":
        job_id = await JobService(db).create_job(
            "delete_records_from_site",
            payload={"site_id": payload.site_id, "directories": [payload.directory]},
        )

        celery_task_id = str(job_id)

        task = delete_records_from_site_task.apply_async(
            task_id=celery_task_id,
            kwargs={"site_id": payload.site_id, "directories": [payload.directory]},
        )

        return {"job_id": job_id, "celery_task_id": task.id}


@router.post("/scan-all-directories", response_model=SiteDirectoriesScanResponse)
async def scan_site_directories(
    payload: SiteDirectoriesScanRequest, db: AsyncSession = Depends(get_db)
):
    directories = await SiteService(db).get_directories_for_site(payload.site_id)
    job_id = await check_directories_and_create_import_job(
        db, payload.site_id, directories
    )
    return {"job_id": job_id}


@router.post("/scan-directory", response_model=SiteDirectoryScanResponse)
async def scan_site_directory(
    payload: SiteDirectoryScanRequest, db: AsyncSession = Depends(get_db)
):
    job_id = await check_directories_and_create_import_job(
        db, payload.site_id, [payload.directory]
    )
    return {"job_id": job_id}


@router.post("/create-data-report", response_model=SiteDataReportResponse)
async def create_data_report(
    payload: CreateDataReportRequest, db: AsyncSession = Depends(get_db)
):
    job_service = JobService(db)
    job_id = await job_service.create_job(
        f"{task_topic.CREATE_SITE_DATA_REPORT.value}",
        payload={
            "site_id": payload.site_id,
        },
    )

    celery_task_id = str(job_id)

    create_site_data_report_task.apply_async(
        task_id=celery_task_id,
        kwargs={"site_id": payload.site_id},
    )
    return {"job_id": job_id}


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
