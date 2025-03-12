import os
import time
from backend.worker.tasks.utils.site_tasks import wait_for_lock_and_create_report
import soundfile as sf
from pathlib import Path
from datetime import datetime
from celery.utils.log import get_task_logger


from backend.worker.app import app
from backend.shared.models.db.models import Records, SiteDirectories
from backend.worker.tools import parse_datetime
from backend.worker.settings import WorkerSettings
from backend.worker.services.job_service import JobService
from backend.worker.database import db_session
from backend.worker.tasks.base_task import BaseTask

logger = get_task_logger(__name__)
settings = WorkerSettings()

# Configure logger level from settings
logger.setLevel(settings.log_level)


@app.task(name="delete_records_from_site", bind=True, base=BaseTask, track_started=True)
def delete_records_from_site_task(self, site_id: int, directories: list[str]):
    job_id = self.request.id
    session = db_session()

    logger.info(f"Deleting records from site {site_id} in directories {directories}")

    try:
        deleted_records = 0
        counter = 0
        for directory in directories:
            if self.check_revoked():
                return {
                    "status": "revoked",
                    "task_id": job_id,
                    "message": "Task was revoked.",
                }

            # Direct filtered delete
            deleted_count = (
                session.query(Records)
                .filter(
                    Records.site_id == site_id,
                    Records.filepath.like(f"{directory}%"),
                )
                .delete(synchronize_session=False)
            )

            session.commit()
            deleted_records += deleted_count
            counter += 1
            logger.info(f"Deleted {deleted_count} records from {directory}")
            # Progress updates with separate short-lived session

            try:

                JobService.update_job_progress_by_counter(
                    session, job_id, counter, len(directories)
                )
                session.commit()
                time.sleep(1)
            except Exception as e:
                session.rollback()
                logger.error(f"Progress update failed: {str(e)}")

        if deleted_records == 0:
            return "No records found to delete"
        wait_for_lock_and_create_report(job_id, site_id, session, logger)
    except Exception as e:
        session.rollback()
        JobService.set_job_error(session, job_id, str(e))
        logger.error(f"Error deleting records: {str(e)}")
        raise e

    return {
        "status": "success",
        "message": f"Successfully deleted {deleted_records} records from {len(directories)} directories",
    }
