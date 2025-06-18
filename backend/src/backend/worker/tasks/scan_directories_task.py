import os
import time

from backend.worker.tasks.utils.site_tasks import wait_for_lock_and_create_report
import soundfile as sf
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
logger.setLevel(settings.log_level)
BATCH_SIZE = 100

class DirectoryScanner:
    """Scans directories for audio files based on specified extensions."""
    def __init__(self, base_data_directory: Path, audio_extensions_list: list[str]):
        self.base_data_directory = base_data_directory
        self.audio_extensions_list = audio_extensions_list

    def collect_audio_files(self, directories: list[str]) -> list[Path]:
        """Scans directories for audio files with allowed extensions.

        Args:
            directories (list[str]): Directories to scan (relative to base directory).

        Returns:
            list[Path]: Absolute paths to collected audio files. Empty list if no files found.
        """
        all_files = []
        for directory in directories:
            dir_path = (self.base_data_directory / Path(directory)).resolve()
            if dir_path.is_dir():
                for root, _, files in os.walk(dir_path):
                    all_files.extend(
                        Path(root) / file
                        for file in files
                        if Path(file).suffix.lower() in self.audio_extensions_list
                    )
        return all_files

class AudioFileValidator:
    """Validates audio files against site-specific criteria."""
    def __init__(self, site: Sites):
        self.site = site

    def validate_and_get_props(self, file_path: Path):
        """Validates audio file and returns errors and audio properties.

        Args:
            file_path (Path): Path to the audio file.

        Returns:
            Tuple[List[Dict[str, str]], Optional[Tuple[float, str, int]]]: Errors and (duration, channels, sample rate) or None if validation fails.
        """
        errors = []
        duration = channels = sample_rate = 0

        # Validate filename prefix
        if not file_path.name.startswith(self.site.prefix):
            errors.append({
                "type": f"{RecordErrorsEnum.MISSING_FILE_PREFIX.value}",
                "message": f"Filename must start with {self.site.prefix}",
            })

        # Validate record datetime
        try:
            self._parse_record_datetime(file_path.stem)
        except Exception as e:
            errors.append({
                "type": f"{RecordErrorsEnum.RECORD_DATETIME_FORMAT.value}",
                "message": f"Error parsing record datetime: {str(e)}",
            })

        # Validate audio properties
        try:
            with sf.SoundFile(file_path) as audio:
                duration = audio.frames / audio.samplerate
                channels = str(audio.channels)
                sample_rate = audio.samplerate

                if sample_rate != self.site.sample_rate:
                    errors.append({
                        "type": f"{RecordErrorsEnum.SAMPLERATE_MISSMATCH.value}",
                        "message": f"Sample rate mismatch: {sample_rate} != {self.site.sample_rate}",
                    })
                expected = float(self.site.record_regime_recording_duration)
                allowed = 1 / float(self.site.sample_rate)
                if not (expected - allowed <= duration <= expected + allowed):
                    errors.append({
                        "type": RecordErrorsEnum.DURATION_MISSMATCH.value,
                        "message": f"Duration mismatch: {duration} != {expected}",
                    })
        except Exception as e:
            errors.append({
                "type": RecordErrorsEnum.FILE_READ_ERROR.value,
                "message": f"Error reading file: {str(e)}",
            })

        return errors, (duration, channels, sample_rate) if duration is not None else None

    def _parse_record_datetime(self, filename_stem: str):
        return parse_datetime(filename_stem)

class RecordManager:
    """Manages database records for audio files."""
    def __init__(self, session, site: Sites, settings: WorkerSettings):
        self.session = session
        self.site = site
        self.settings = settings

    def record_exists(self, filename: str):
        """Checks if a record with the given filename exists in the database.

        Args:
            filename (str): The filename to search for.

        Returns:
            sqlalchemy.engine.row.Row | None: The record if it exists, otherwise None. Contains the id and errors columns.

        Raises:
            Exception: If there is an error during the database query.
        """
        try:
            exists = self.session.query(Records.id, Records.errors).filter_by(filename=filename).first()
            logger.info(f"Exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking file existence: {str(e)}")
            raise e

    def create_record(self, file_path: Path, errors, audio_props):
        """Creates a database record for a scanned audio file.

        Args:
            file_path (Path): The absolute path to the audio file.
            errors (list, optional): Errors encountered during processing. Defaults to None.
            audio_props (tuple, optional): Audio duration, channels, and sample rate. Defaults to None.

        Returns:
            Records: A `Records` object representing the audio file's metadata, or None if an error occurred.

        Raises:
            Exception: If any error occurs during the creation or updating of the record.
        """
        try:
            file_path_relative = file_path.relative_to(self.settings.base_data_directory)
            duration, channels, sample_rate = audio_props if audio_props else (None, None, None)
            record = Records(
                site_id=self.site.id,
                filepath=str(file_path_relative),
                filename=file_path.name,
                record_datetime=parse_datetime(file_path.stem),
                duration=duration,
                channels=channels,
                sample_rate=sample_rate,
                mime_type=f"audio/{file_path.suffix[1:].lower()}",
                errors=errors if errors else None,
            )
            return record
        except Exception as e:
            logger.error(f"Error creating or updating record for {file_path}: {e}")
            return None

class JobProgressReporter:
    """Reports the progress of a job and updates its status in the database."""

    def __init__(self, session, job_id: str, logger):
        self.session = session
        self.job_id = job_id
        self.logger = logger

    def update_progress(self, processed_files: int, total_files: int):
        """Updates the progress percentage of the job in the database.

        Args:
            processed_files (int): Number of files processed.
            total_files (int): Total number of files.
        """
        progress = int((processed_files / total_files) * 100)
        try:
            JobService.update_job_progress(self.session, self.job_id, progress)
            self.session.commit()
        except Exception as e:
            self.logger.error(f"Progress update failed: {str(e)}")
            self.logger.debug(f"Job ID: {self.job_id}, Progress: {progress}")
            raise e

    def update_result(self, processed_files: int, total_files: int, added_records: int):
        """Updates the final result of the job in the database.

        Args:
            processed_files (int): Number of files processed.
            total_files (int): Total number of files.
            added_records (int): Number of records added.
        """
        JobService.updateResult(
            self.session,
            self.job_id,
            {
                "total_files": total_files,
                "processed_files": processed_files,
                "added_records": added_records,
            },
        )

    def commit_batch(self, idx: int, total_files: int):
        """Commits the current batch of changes to the database and logs the progress.

        Args:
            idx (int): Index of the last file processed in the batch.
            total_files (int): Total number of files.
        """
        self.session.commit()
        self.logger.info(f"Committed {idx}/{total_files} files")

def get_site(session, site_id: int) -> Sites:
    site = session.query(Sites).filter(Sites.id == site_id).first()
    if not site:
        raise ValueError(f"Site with id {site_id} not found")
    session.expunge(site)
    return site

@app.task(
    name=f"{task_topic.SCAN_DIRECTORIES.value}",
    bind=True,
    base=BaseTask,
    track_started=True,
    queue="db_worker_queue",
)
def scan_directories_task(self, site_id: int, directories: list[str]):
    """Celery task to scan directories, validate audio files, and store them in the database.

        Args:
            site_id (int): The ID of the site.
            directories (list[str]): Directories to scan.

        Returns:
            dict: Task status and message.
    """
    job_id = self.request.id
    session = db_session()

    try:
        site = get_site(session, site_id)
        scanner = DirectoryScanner(settings.base_data_directory, settings.audio_extensions_list)
        validator = AudioFileValidator(site)
        record_manager = RecordManager(session, site, settings)
        reporter = JobProgressReporter(session, job_id, logger)

        all_files = scanner.collect_audio_files(directories)
        total_files = len(all_files)
        logger.info(f"Total files to process: {total_files}")

        if total_files == 0:
            return {"status": "success", "message": "No files found in directories"}

        processed_files = 0
        added_records = 0

        for idx, file_path in enumerate(all_files, 1):
            if self.check_revoked():
                time.sleep(1)
                return {
                    "status": "revoked",
                    "message": "Task was revoked",
                    "processed_files": processed_files,
                    "added_records": added_records,
                }

            try:
                errors, audio_props = validator.validate_and_get_props(file_path)
                record = record_manager.create_record(file_path, errors, audio_props)

                if record:
                    if record_manager.record_exists(file_path.name) is not None:
                        logger.info(f"Updating record: {record}")
                        session.merge(record)
                    else:
                        session.add(record)
                    added_records += 1

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")

            processed_files += 1

            if (processed_files % max(1, total_files // 100)) == 0:
                reporter.update_progress(processed_files, total_files)

            reporter.update_result(processed_files, total_files, added_records)

            if added_records % BATCH_SIZE == 0:
                reporter.commit_batch(idx, total_files)

        if session.dirty or session.new or session.deleted:
            session.commit()

        wait_for_lock_and_create_report(job_id, site_id, session, logger)
        JobService.update_job_progress(session, job_id, 100)

        return {
            "status": "success",
            "message": f"Successfully scanned {len(directories)} directories for site {site_id}",
        }

    except Exception as e:
        session.rollback()
        JobService.set_job_error(session, job_id, str(e))
        logger.error(f"Task failed: {str(e)}")
        raise e
