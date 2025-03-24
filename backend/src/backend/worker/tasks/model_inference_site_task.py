import os
import shutil
import time
import pandas
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from backend.worker.tasks.utils.site_tasks import wait_for_lock_and_create_report
import soundfile as sf
from pathlib import Path
from datetime import datetime
from celery.utils.log import get_task_logger
from celery import states

from backend.worker.app import app
from backend.shared.models.db.models import Models, Records, ModelInferenceResults

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
    queue="inference_queue",
)
def model_inference_site_task(
    self, site_id: int, model_id: int, start_datetime: datetime, end_datetime: datetime
):
    job_id = self.request.id
    session = db_session()
    # create temp directories for the pathes for host and container
    # If you start an container inside a container, you need to mount the host directory to the container
    # and use the host directory for the output and input
    job_temp_dir = os.path.join(settings.tmp_dir, job_id)
    host_model_output_dir = os.path.join(settings.host_tmp_dir, job_id)
    input_paths_file = os.path.join(settings.tmp_dir, job_id, "inputPaths.txt")
    host_input_paths_file = os.path.join(
        settings.host_tmp_dir, job_id, "inputPaths.txt"
    )

    try:
        # get model string
        model = session.query(Models.name).filter(Models.id == model_id).first()
        if not model:
            raise Exception(f"Model {model_id} not found")
        file_counter = 0

        # Get current user and group IDs to make the docker output files readable
        uid = os.getuid()
        gid = os.getgid()

        logger.info(f"Fetching records for site {site_id} and model {model_id}")
        total_count = (
            session.query(func.count(Records.id))
            .join(
                ModelInferenceResults,
                (Records.id == ModelInferenceResults.record_id)
                & (ModelInferenceResults.model_id == model_id),
                isouter=True,
            )
            .filter(Records.site_id == site_id, ModelInferenceResults.id.is_(None))
            .filter(Records.record_datetime >= start_datetime)
            .filter(Records.record_datetime <= end_datetime)
            .scalar()
        )
        # create the tmp directory
        logger.info(
            f"Found {total_count} records to process for site {site_id} and model {model.name}"
        )
        os.makedirs(job_temp_dir, exist_ok=True)
        if total_count == 0:
            JobService.update_job_progress(session, job_id, 100)
            return {
                "status": "success",
                "message": f"No records to process for site {site_id}",
            }

        while total_count > file_counter:
            if self.check_revoked():
                time.sleep(1)
                # Wait for 1 second to ensure the task is revoked
                return {
                    "status": "revoked",
                    "message": "Task was revoked.",
                }

            records = (
                session.query(Records.id, Records.filepath, Records.filename)
                .outerjoin(
                    ModelInferenceResults,
                    (Records.id == ModelInferenceResults.record_id)
                    & (ModelInferenceResults.model_id == model_id),
                )
                .filter(Records.site_id == site_id)
                .filter(ModelInferenceResults.id.is_(None))
                .limit(BATCH_SIZE)
                .all()
            )
            if len(records) == 0:
                break

            # Prepare inputPaths.txt file for the model
            record_name_to_id = {}
            with open(input_paths_file, "w") as f:
                for record in records:
                    f.write(
                        os.path.join(settings.host_base_data_directory, record.filepath)
                        + "\n"
                    )
                    record_name_to_id[record.filename] = record.id

            # run os command to run the model
            command = f"""docker run -v /var/run/docker.sock:/var/run/docker.sock \
                        --rm -v {host_input_paths_file}:/app/inputPaths.txt \
                        -v {host_model_output_dir}:/output \
                        -v {settings.host_base_data_directory}:/data \
                        { f"--gpus {settings.gpus}" if settings.gpus != "none" else "" } \
                        models -i /app/inputPaths.txt -m {model.name} -o /output -ov {host_model_output_dir} --removeTemporaryResultFile -chown {uid}:{gid} --f pkl -on output"""

            logger.info(f"Running command: {command}")
            os.system(command)

            # read the output.pkl file and add the results to the database
            df = pandas.read_pickle(os.path.join(job_temp_dir, "output.pkl"))
            for _, row in df.iterrows():
                session.add(
                    ModelInferenceResults(
                        record_id=record_name_to_id[row["filename"]],
                        model_id=model_id,
                        start_time=row["start_time"],
                        end_time=row["end_time"],
                        confidence=row["confidence"],
                        label_id=row["label_id"],
                    )
                )
            session.commit()
            file_counter += len(records)

            JobService.update_job_progress_by_counter(
                session, job_id, file_counter, total_count
            )
            # delete all files in the job_temp_dir for the next batch
            for file in os.listdir(job_temp_dir):
                os.remove(os.path.join(job_temp_dir, file))
            JobService.updateResult(session, job_id, {"inferred_records": file_counter})
        JobService.update_job_progress(session, job_id, 100)

    except Exception as e:
        session.rollback()
        JobService.set_job_error(session, job_id, str(e))
        logger.error(f"Task failed: {str(e)}")
        raise e
    finally:
        # Uncomment this when you're ready to clean up

        shutil.rmtree(job_temp_dir)
    return {
        "status": "success",
        "message": f"Successfully analyzed {file_counter} records for site {site_id}",
    }
