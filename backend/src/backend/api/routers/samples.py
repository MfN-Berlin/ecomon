from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.services.directory_service import DirectoryService
from backend.api.models.models import (
    JobActionResponse,
    CreateVoucherRequest,
)
from backend.api.services.job_service import JobService
from backend.api.settings import ApiSettings
from backend.worker.tasks.create_voucher_task import (
    create_voucher_task,
)

from backend.api.database import get_db
from backend.shared.consts import task_topic

router = APIRouter(prefix="/samples", tags=["samples"])
directory_service = DirectoryService(ApiSettings())


###
# Endpoints
###


@router.post("/create-voucher", response_model=JobActionResponse)
async def create_voucher(
    payload: CreateVoucherRequest, db: AsyncSession = Depends(get_db)
):
    job_service = JobService(db)

    # Convert datetime objects to ISO format strings for JSON serialization
    start_datetime_str = (
        payload.start_datetime.isoformat() if payload.start_datetime else None
    )
    end_datetime_str = (
        payload.end_datetime.isoformat() if payload.end_datetime else None
    )

    job_id = await job_service.create_job(
        f"{task_topic.CREATE_VOUCHER.value}",
        metadata={
            "site_id": payload.site_id,
            "model_id": payload.model_id,
            "label_ids": payload.label_ids,
            "sample_count": payload.sample_count,
            "start_datetime": start_datetime_str,
            "end_datetime": end_datetime_str,
        },
    )

    celery_task_id = str(job_id)

    create_voucher_task.apply_async(
        task_id=celery_task_id,
        kwargs={
            "site_id": payload.site_id,
            "model_id": payload.model_id,
            "label_ids": payload.label_ids,
            "sample_count": payload.sample_count,
            "start_datetime": start_datetime_str,
            "end_datetime": end_datetime_str,
            "audio_padding_ms": payload.audio_padding_ms,
            "high_pass_filter_frequency_hz": payload.high_pass_filter_frequency_hz,
        },
    )
    return {"job_id": job_id}
