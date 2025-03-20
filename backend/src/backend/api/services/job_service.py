import logging
from logging.config import dictConfig
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.models.db.models import Jobs
from backend.api.logger_config import get_log_config
from backend.shared.models.job_status import JobStatus

dictConfig(get_log_config(timestamp=True))
logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(self, job_topic: str, metadata: Optional[dict] = None) -> str:
        """
        Create a new job db entry with a unique ID

        Args:
            job_type: Type of job from JobType enum
            metadata: Optional metadata about the job
        """
        job = Jobs(
            topic=job_topic,
            metadata_=metadata,
            status=JobStatus.PENDING.value,
        )

        logger.info(
            f"Creating job: {job} on topic: {job_topic} with metadata: {metadata}"
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job.id

    async def set_job_error(self, job_id: str, error: str):
        """
        Set the job status to failed and add an error message

        Args:
            job_id: The ID of the job to update
            error: The error message
        """
        job = await self.get_job(job_id)
        if job:
            job.status = JobStatus.FAILED.value
            job.error = error
            await self.db.commit()
            return job
        else:
            raise ValueError(f"Job with id {job_id} not found")

    async def get_job(self, job_id: str) -> Jobs:
        """
        Get a job by its ID

        Args:
            job_id: The ID of the job to get
        """
        async with self.db.begin():
            result = await self.db.execute(select(Jobs).filter(Jobs.id == job_id))
            return result.scalar_one_or_none()
