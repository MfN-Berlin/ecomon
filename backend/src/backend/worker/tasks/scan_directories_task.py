import os
import time

from backend.worker.tasks.utils.site_tasks import wait_for_lock_and_create_report
import soundfile as sf
from pathlib import Path
from datetime import datetime
from celery.utils.log import get_task_logger
from celery import states

from backend.worker.app import app
from backend.shared.models.db.models import Records, SiteDirectories

from backend.worker.tools import parse_datetime
from backend.worker.settings import WorkerSettings
from backend.worker.services.job_service import JobService

from backend.worker.database import db_session
from backend.worker.tasks.base_task import BaseTask


from backend.shared.consts import task_topic

logger = get_task_logger(__name__)
settings = WorkerSettings()

# Configure logger level from settings
logger.setLevel(settings.log_level)


BATCH_SIZE = 100


@app.task(
    name=f"{task_topic.SCAN_DIRECTORIES.value}",
    bind=True,
    base=BaseTask,
    track_started=True,
)
def scan_directories_task(self, site_id: int, directories: list[str]):
    job_id = self.request.id
    session = db_session()
    try:
        all_files = []
        for directory in directories:
            dir_path = (settings.base_data_directory / Path(directory)).resolve()
            if dir_path.is_dir():
                for root, _, files in os.walk(dir_path):
                    all_files.extend([Path(root) / file for file in files])

        total_files = len(all_files)
        logger.info(f"Total files to process: {total_files}")
        if total_files == 0:
            return "No files found in directories"

        current_batch = 0
        processed_files = 0

        for idx, file_path in enumerate(all_files, 1):

            if self.check_revoked():
                time.sleep(1)
                # Wait for 1 second to ensure the task is revoked

                return {
                    "status": "revoked",
                    "message": "Task was revoked.",
                }
            if file_path.suffix.lower() not in settings.audio_extensions_list:
                processed_files += 1
                continue

            try:
                # Simplified exists check
                exists = (
                    session.query(Records.id).filter_by(filepath=str(file_path)).first()
                    is not None
                )
                file_path_relative_to_base_data_directory = file_path.relative_to(
                    settings.base_data_directory
                )
            except Exception as e:
                logger.error(f"Error checking file existence: {str(e)}")
                raise e

            if not exists:
                try:
                    record_datetime = parse_datetime(file_path.stem)
                    with sf.SoundFile(file_path) as audio:
                        duration = audio.frames / audio.samplerate
                        channels = str(audio.channels)
                        sample_rate = audio.samplerate

                    record = Records(
                        site_id=site_id,
                        filepath=str(file_path_relative_to_base_data_directory),
                        filename=file_path.name,
                        record_datetime=record_datetime,
                        duration=float(duration),
                        channels=channels,
                        sample_rate=sample_rate,
                        mime_type=f"audio/{file_path.suffix[1:].lower()}",
                    )

                    session.add(record)
                    current_batch += 1

                    if current_batch >= BATCH_SIZE:
                        session.commit()
                        session.close()
                        db_session.remove()
                        session = db_session()
                        current_batch = 0
                        logger.info(f"Committed {idx}/{total_files} files")

                except Exception as e:
                    session.rollback()
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    current_batch = 0

            if (processed_files % max(1, total_files // 100)) == 0:
                progress = int((processed_files / total_files) * 100)
                try:
                    JobService.update_job_progress(session, job_id, progress)
                    session.commit()
                except Exception as e:
                    logger.error(f"Progress update failed: {str(e)}")
                    # Additional logging for debugging
                    logger.debug(f"Job ID: {job_id}, Progress: {progress}")
                    raise e

            processed_files += 1
            time.sleep(0.1)

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
        "message": f"Successfully scanned {len(directories)} directories for site {site_id}",
    }
