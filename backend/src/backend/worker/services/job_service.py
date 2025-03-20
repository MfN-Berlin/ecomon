from datetime import datetime
from typing import Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update, cast, exists
from sqlalchemy.dialects.postgresql import JSONB, insert

from backend.shared.models.db.models import Jobs
from backend.shared.models.job_status import JobStatus
from backend.shared.consts import task_topic


class JobService:
    @staticmethod
    def create_job(
        session: Session, job_topic: str, metadata: Optional[dict] = None
    ) -> str:
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

        session.add(job)
        session.commit()
        return job.id

    @staticmethod
    def get_job(session: Session, job_id: str) -> Jobs:
        """
        Retrieve a job by its ID

        Args:
            session: The database session
            job_id: The ID of the job to retrieve

        Returns:
            The Job object if found

        Raises:
            ValueError: If the job is not found
        """
        job = session.query(Jobs).filter(Jobs.id == job_id).first()
        if not job:
            raise ValueError(f"Job with id {job_id} not found")
        return job

    @staticmethod
    def update_job_status(session: Session, job_id: str, status: str):
        """
        Update the status of an existing job

        Args:
            session: The database session
            job_id: The ID of the job to update
            status: New status (e.g., 'running', 'done', 'failed')
            result: Optional result data
        """
        session.query(Jobs).filter(Jobs.id == job_id).update({"status": status})
        session.commit()

    @staticmethod
    def set_job_error(session: Session, job_id: str, error_msg: str):
        """
        Set the job status to failed and add an error message

        Args:
            session: The database session
            job_id: The ID of the job to update
            error_msg: The error message
        """
        # Use SQLAlchemy core update to avoid ORM issues

        JobService.update_job_status(session, job_id, JobStatus.FAILED.value)

    @staticmethod
    def set_job_running(session: Session, job_id: str):
        """
        Set the job status to running

        Args:
            session: The database session
            job: The job object to update
        """

        JobService.update_job_status(session, job_id, JobStatus.RUNNING.value)

    @staticmethod
    def set_job_done(session: Session, job_id: str):
        """
        Set the job status to done and add a result

        Args:
            session: The database session
            job: The job object to update
            result: The result data
        """
        JobService.update_job_status(session, job_id, JobStatus.DONE.value)

    @staticmethod
    def set_job_canceled(session, job_id):
        """Set a job's status to canceled"""
        JobService.update_job_status(session, job_id, JobStatus.CANCELED.value)

    @staticmethod
    def update_job_progress_by_counter(
        session: Session, job_id: str, current: int, total: int
    ):
        """
        Set the progress of a job by file count
        """
        progress = int((current / total) * 100)
        JobService.update_job_progress(session, job_id, progress)
        session.commit()

    @staticmethod
    def update_job_progress(session: Session, job_id: str, progress: int):
        """
        Update the progress of a job

        Args:
            session: The database session
            job_id: The ID of the job to update
            progress: The new progress value (0-100)
        """

        session.query(Jobs).filter(Jobs.id == job_id).update({"progress": progress})
        session.commit()

    @staticmethod
    def reset_unfinished_jobs(session: Session):
        """
        Find all jobs with status 'running' and set them to 'failed' with an error message
        """
        running_jobs = (
            session.query(Jobs)
            .filter(
                Jobs.status.notin_(
                    [
                        JobStatus.DONE.value,
                        JobStatus.FAILED.value,
                        JobStatus.CANCELED.value,
                    ]
                )
            )
            .all()
        )

        for job in running_jobs:
            session.query(Jobs).filter(Jobs.id == job.id).update(
                {
                    "status": JobStatus.FAILED.value,
                    "error": {"msg": "Found unfinished on startup"},
                }
            )

        session.commit()
        return len(running_jobs)

    @staticmethod
    def does_other_site_job_exists(
        session: Session, own_task_id: str, topics: list[str], site_id: int
    ) -> bool:
        """
        Check if there is a running job for another site
        """

        # Construct the query
        query = session.query(Jobs).filter(
            Jobs.topic.in_(topics),
            cast(Jobs.metadata_, JSONB)["site_id"] == str(site_id),
            Jobs.status.notin_([JobStatus.DONE.value, JobStatus.FAILED.value]),
            Jobs.id != own_task_id,
        )
        exists_query = session.query(query.exists()).scalar()

        return exists_query

    @staticmethod
    def updateResult(session: Session, job_id: int, result: dict) -> Jobs:
        """
        Get a job by id and update the result
        """
        session.query(Jobs).filter(Jobs.id == job_id).update({"result": result})
        session.commit()
        return
