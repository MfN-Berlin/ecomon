import os
import time
from sqlalchemy.orm import selectinload
from backend.worker.tasks.utils.site_tasks import wait_for_lock_and_create_report
import soundfile as sf
from pathlib import Path
from datetime import datetime
from celery.utils.log import get_task_logger
from celery import states

from backend.worker.app import app
from backend.shared.models.db.models import Records, ModelInferenceResults

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
    name=f"{task_topic.MODEL_INFERENCE_SITE.value}",
    bind=True,
    base=BaseTask,
    track_started=True,
)
def model_inference_site_task(self, site_id: int, model_id: int):
    job_id = self.request.id
    session = db_session()
    try:
        file_counter = 0
        logger.info(f"Fetching records for site {site_id} and model {model_id}")
        records = (
            session.query(Records)
            .options(selectinload(Records.model_inference_results))
            .outerjoin(
                ModelInferenceResults,
                (Records.id == ModelInferenceResults.record_id)
                & (ModelInferenceResults.model_id == model_id),
            )
            .filter(Records.site_id == site_id)
            .filter(ModelInferenceResults.id.is_(None))
            .all()
        )
        logger.info(f"Found {len(records)} records to process")
        # Prepare inputPaths.txt file for the model

        input_paths_file = os.path.join(settings.tmp_dir, job_id, "inputPaths.txt")
        os.makedirs(os.path.join(settings.tmp_dir, job_id), exist_ok=True)
        logger.info(f"Input paths file: {input_paths_file}")
        model_output_dir = os.path.join(settings.tmp_dir, job_id, "model_output")
        logger.info(f"Model output directory: {model_output_dir}")
        os.makedirs(model_output_dir, exist_ok=True)
        logger.info(f"Data Base Directory: {settings.base_data_directory}")

        with open(input_paths_file, "w") as f:
            for record in records:
                f.write(os.path.join("/data", record.filepath) + "\n")

        # run os command to run the model
        command = f"""docker run -v /var/run/docker.sock:/var/run/docker.sock \
                    -v {input_paths_file}:/app/inputPaths.txt \
                    -v {model_output_dir}:/output \
                    -v {settings.base_data_directory}:/data\
                    --gpus all \
                    runmodel -i /app/inputPaths.txt -o /output"""
        logger.info(f"Running command: {command}")
        os.system(command)

        # Fetch a chunk of records that do NOT have an inference for the current model_id.

        file_counter += len(records)

    except Exception as e:
        session.rollback()
        JobService.set_job_error(session, job_id, str(e))
        logger.error(f"Task failed: {str(e)}")
        raise e

    return {
        "status": "success",
        "message": f"Successfully analyzed {file_counter} records for site {site_id}",
    }
