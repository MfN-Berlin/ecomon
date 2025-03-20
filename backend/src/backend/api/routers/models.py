from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.services.directory_service import DirectoryService
from backend.api.models.directory import DirectoryInfo
from backend.api.models.models import (
    AnalyzeSiteRequest,
    AnalyzeSiteResponse,
)
from backend.api.services.job_service import JobService
from backend.api.services.site_service import SiteService
from backend.api.settings import ApiSettings
from backend.worker.tasks.model_inference_site_task import (
    model_inference_site_task,
)

from backend.api.database import get_db
from celery.result import AsyncResult
from backend.shared.consts import task_topic

router = APIRouter(prefix="/models", tags=["models"])
directory_service = DirectoryService(ApiSettings())


###
# Endpoints
###


@router.post("/analyse-site-timespan", response_model=AnalyzeSiteResponse)
async def analyse_site_timespan(
    payload: AnalyzeSiteRequest, db: AsyncSession = Depends(get_db)
):
    job_service = JobService(db)
    job_id = await job_service.create_job(
        f"{task_topic.MODEL_INFERENCE_SITE  .value}",
        metadata={
            "site_id": payload.site_id,
            "model_id": payload.model_id,
        },
    )

    celery_task_id = str(job_id)

    model_inference_site_task.apply_async(
        task_id=celery_task_id,
        kwargs={"site_id": payload.site_id, "model_id": payload.model_id},
    )
    return {"job_id": job_id}
