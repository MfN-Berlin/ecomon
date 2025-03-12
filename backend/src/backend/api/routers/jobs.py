from typing import Any
from fastapi import APIRouter, Depends, status, HTTPException
from celery.result import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.database import get_db
import asyncio
from backend.api.services.task_service import TaskService

router = APIRouter(prefix="/jobs", tags=["jobs"])
task_service = TaskService()


@router.post("/delete/{job_id}", status_code=status.HTTP_200_OK)
async def delete_job(job_id: str, metadata: Any, db: AsyncSession = Depends(get_db)):
    """
    Delete a job from the database
    """
    result = AsyncResult(job_id)
    if not result.ready():  # Check if job is still running
        print(f"Job {job_id} is still running, cannot delete")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a running job. Cancel it first.",
        )

    try:
        ...
        pass
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found or could not be deleted: {str(e)}",
        )


@router.post("/cancel/{job_id}", status_code=status.HTTP_200_OK)
async def cancel_job(job_id: str):
    """
    Attempt soft cancellation, check every second, fall back to hard cancellation after 30 seconds
    """
    print(f"Cancelling job {job_id}")
    return await task_service.cancel_task(job_id)
