import os
import time
import numpy as np
import soundfile as sf
from pathlib import Path
from datetime import datetime, timedelta
from celery.utils.log import get_task_logger
from celery import states
import shutil
import uuid
from sqlalchemy import func, desc, text
from sqlalchemy.dialects.postgresql import JSONB
import json

from backend.worker.app import app
from backend.shared.models.db.models import (
    Records,
    SiteReports,
    Sites,
    ModelInferenceResults,
    Labels,
)
from backend.worker.settings import WorkerSettings
from backend.worker.services.job_service import JobService
from backend.worker.database import db_session
from backend.worker.tasks.base_task import BaseTask
from backend.shared.consts import task_topic
from backend.shared.record_snippet import SupportedFormat, save_snippet_to_file

logger = get_task_logger(__name__)
settings = WorkerSettings()

# Configure logger level from settings
logger.setLevel(settings.log_level)


@app.task(
    name=f"{task_topic.CREATE_VOUCHER.value}",
    bind=True,
    base=BaseTask,
    track_started=True,
    queue="db_worker_queue",
)
def create_voucher_task(
    self,
    site_id: int,
    model_id: int,
    label_ids: list[int],
    sample_count: int,
    start_datetime: datetime,
    end_datetime: datetime,
    audio_padding_ms: int,
    high_pass_filter_frequency_hz: int,
):
    job_id = self.request.id
    session = db_session()

    try:
        JobService.set_job_running(session, job_id)
        session.commit()

        logger.info(
            f"Creating voucher for site {site_id} with model {model_id}"
            f" and label_ids {label_ids} and sample_count {sample_count}"
            f" start_datetime {start_datetime} end_datetime {end_datetime}"
            f" audio_padding_ms {audio_padding_ms} high_pass_filter_frequency_hz {high_pass_filter_frequency_hz}"
        )

        # Create a unique directory for temporary files
        tmp_dir = Path(settings.tmp_dir) / f"voucher_{job_id}"
        os.makedirs(tmp_dir, exist_ok=True)

        # Generate output filename
        site = session.query(Sites).filter(Sites.id == site_id).first()
        if not site:
            raise ValueError(f"Site with ID {site_id} not found")

        # Process each label
        total_labels = len(label_ids)
        for idx, label_id in enumerate(label_ids):
            label = session.query(Labels).filter(Labels.id == label_id).first()
            if not label:
                logger.warning(f"Label with ID {label_id} not found, skipping")
                continue

            logger.info(f"Processing label: {label.name} ({idx+1}/{total_labels})")

            # Get top samples for this label
            samples = (
                session.query(
                    Records.filepath,
                    Records.filename,
                    Records.record_datetime,
                    Records.duration,
                    ModelInferenceResults.start_time,
                    ModelInferenceResults.end_time,
                    ModelInferenceResults.confidence,
                )
                .join(
                    ModelInferenceResults, Records.id == ModelInferenceResults.record_id
                )
                .filter(
                    Records.site_id == site_id,
                    ModelInferenceResults.model_id == model_id,
                    ModelInferenceResults.label_id == label_id,
                    Records.record_datetime.between(start_datetime, end_datetime),
                )
                .order_by(desc(ModelInferenceResults.confidence))
                .limit(sample_count)
                .all()
            )

            # Create a directory for this label
            label_dir = tmp_dir / label.name
            os.makedirs(label_dir, exist_ok=True)

            # Process each sample
            for sample in samples:
                (
                    filepath,
                    filename,
                    record_datetime,
                    duration,
                    start_time,
                    end_time,
                    confidence,
                ) = sample
                logger.info(
                    f"Processing sample: {filename} with start_time {start_time} and end_time {end_time}, confidence {confidence}"
                )
                # Create output filename
                stem, ext = os.path.splitext(filename)
                out_filename = (
                    f"{stem}_S{format_time(start_time)}_E{format_time(end_time)}{ext}"
                )
                out_filepath = label_dir / out_filename

                # Extract audio segment
                save_snippet_to_file(
                    Path(settings.base_data_directory) / filepath,
                    str(out_filepath),
                    SupportedFormat.WAV,
                    start_time,
                    end_time,
                    audio_padding_ms,
                    high_pass_filter_frequency_hz,
                )

                # # Create metadata file
                # with open(label_dir / f"{stem}_metadata.json", "w") as f:
                #     json.dump(
                #         {
                #             "label": label.name,
                #             "filename": filename,
                #             "record_datetime": record_datetime.isoformat(),
                #             "start_time": start_time,
                #             "end_time": end_time,
                #             "duration": duration,
                #             "confidence": confidence,
                #             "audio_padding": audio_padding,
                #         },
                #         f,
                #         indent=2,
                #     )

            # Update progress
            progress = int(((idx + 1) / total_labels) * 100)
            JobService.update_job_progress(session, job_id, progress)
            session.commit()

        results_dir = Path(settings.results_directory) / f"voucher_{job_id}"
        result_filename = (
            f"voucher_{site.prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        result_filepath = results_dir / result_filename
        os.makedirs(results_dir, exist_ok=True)

        # Create zip file
        create_zip_archive(tmp_dir, result_filepath)

        # Clean up temporary directory
        shutil.rmtree(tmp_dir)

        # Update job status
        JobService.updateResult(
            session,
            job_id,
            {"filepath": str(result_filepath), "filename": result_filename},
        )
        session.commit()

        return {
            "status": "success",
            "message": f"Successfully created voucher for site {site_id}",
            "filepath": str(result_filepath),
            "filename": result_filename,
        }

    except Exception as e:
        logger.error(f"Error creating voucher: {str(e)}", exc_info=True)
        session.rollback()
        JobService.set_job_error(session, job_id, str(e))
        # Clean up temporary directory if it exists
        if "tmp_dir" in locals() and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise e


def format_time(seconds):
    """Format seconds to MM_SS_ms format"""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02d}_{seconds:05.2f}".replace(".", "_")


def create_zip_archive(source_dir, output_path):
    """Create a zip archive from a directory"""
    shutil.make_archive(
        os.path.splitext(output_path)[0], "zip", source_dir  # Remove .zip extension
    )
