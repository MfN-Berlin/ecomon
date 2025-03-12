from backend.worker.services.job_service import JobService
from sqlalchemy.orm import Session
from backend.shared.consts import task_topic
from backend.worker.tasks.create_site_data_report_task import (
    create_site_data_report_task,
)


class TaskCreator:
    @staticmethod
    def create_site_data_report_task(session: Session, site_id: int):
        # Create a job in database, get a unique job_id
        job_id = JobService.create_job(
            session,
            f"{task_topic.CREATE_SITE_DATA_REPORT.value}",
            payload={
                "site_id": site_id,
            },
        )

        celery_task_id = str(job_id)

        task = create_site_data_report_task.apply(
            task_id=celery_task_id + "",  # so Celery task_id and DB job_id match
            kwargs={
                "site_id": site_id,
            },
        )

        return job_id
