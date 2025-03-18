from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.services.directory_service import DirectoryService
from backend.api.models.directory import DirectoryInfo
from backend.api.models.site import (
    AnalyzeSiteRequest,
    AnalyzeSiteResponse,
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

router = APIRouter(prefix="/models", tags=["models"])
directory_service = DirectoryService(ApiSettings())


###
# Endpoints
###


@router.post("/analyze-site")
async def analyze_site(payload: AnalyzeSiteRequest, db: AsyncSession = Depends(get_db)):

    return {"job_id": job_id, "celery_task_id": task.id}
