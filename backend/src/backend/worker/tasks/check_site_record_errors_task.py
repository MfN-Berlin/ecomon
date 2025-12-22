import time

from backend.worker.tasks.utils.site_tasks import wait_for_lock_and_create_report

from pathlib import Path

from celery.utils.log import get_task_logger

from backend.worker.app import app
from backend.shared.models.db.models import Records, Sites

from backend.worker.tools import parse_datetime
from backend.worker.settings import WorkerSettings
from backend.worker.services.job_service import JobService

from backend.worker.database import db_session
from backend.worker.tasks.base_task import BaseTask
from backend.shared.models.db.record_error import RecordErrorsEnum

from backend.shared.consts import task_topic

logger = get_task_logger(__name__)
settings = WorkerSettings()

# Configure logger level from settings
logger.setLevel(settings.log_level)


BATCH_SIZE = 1000


@app.task(
    name=f"{task_topic.CHECK_SITE_RECORD_ERRORS.value}",
    bind=True,
    base=BaseTask,
    track_started=True,
    queue="db_worker_queue",
)
def check_site_record_errors_task(self, site_id: int):
    job_id = self.request.id
    session = db_session()

    try:
        site = session.query(Sites).filter(Sites.id == site_id).first()
        if not site:
            raise ValueError(f"Site with id {site_id} not found")
        # detach site from session
        session.expunge(site)
        offset = 0

        total_files = session.query(Records).filter(Records.site_id == site_id).count()
        processed_files = 0

        while True:
            records = (
                session.query(Records)
                .filter(Records.site_id == site_id)
                .order_by(Records.id)
                .limit(1000)
                .offset(offset)
                .all()
            )
            if not records:
                break
            for record in records:
                if self.check_revoked():
                    time.sleep(1)
                    # Wait for 1 second to ensure the task is revoked

                    return {
                        "status": "revoked",
                        "message": "Task was revoked.",
                    }

                errors = []
                # Validate filename prefix
                if not record.filename.startswith(site.prefix):
                    errors.append(
                        {
                            "type": f"{RecordErrorsEnum.MISSING_FILE_PREFIX.value}",
                            "message": f"Filename must start with {site.prefix}",
                        }
                    )

                try:

                    parse_datetime(Path(record.filename).stem)
                except Exception as e:
                    errors.append(
                        {
                            "type": f"{RecordErrorsEnum.RECORD_DATETIME_FORMAT.value}",
                            "message": f"Error parsing record datetime: {str(e)}",
                        }
                    )

                duration = float(record.duration)
                sample_rate = float(record.sample_rate)
                if sample_rate != site.sample_rate:
                    errors.append(
                        {
                            "type": f"{RecordErrorsEnum.SAMPLERATE_MISMATCH.value}",
                            "message": f"Sample rate mismatch: {sample_rate} != {site.sample_rate}",
                        }
                    )
                if (  # sometimes the duration is off by a fraction off 1/sample_rate
                    duration + (1 / float(site.sample_rate))
                    < site.record_regime_recording_duration
                    or duration - (1 / float(site.sample_rate))
                    > site.record_regime_recording_duration
                ):
                    errors.append(
                        {
                            "type": RecordErrorsEnum.DURATION_MISMATCH.value,
                            "message": f"Duration mismatch: {duration} != {site.record_regime_recording_duration} ",
                        }
                    )

                record.errors = errors if len(errors) > 0 else None
                processed_files += 1

            progress = int((processed_files / total_files) * 100)
            JobService.update_job_progress(session, job_id, progress)
            JobService.updateResult(
                session,
                job_id,
                {
                    "total_files": total_files,
                    "processed_files": processed_files,
                },
            )
            session.commit()
            offset += BATCH_SIZE

        if session.dirty or session.new or session.deleted:
            session.commit()

        # Attempt to acquire the lock with a timeout
        wait_for_lock_and_create_report(job_id, site_id, session, logger)
        JobService.update_job_progress(session, job_id, 100)

    except Exception as e:
        session.rollback()
        JobService.set_job_error(session, job_id, str(e))
        logger.error(f"Task failed: {str(e)}")
        raise e

    return {
        "status": "success",
        "message": f"Successfully checked {len(records)} corrupted records for site {site_id}",
    }
