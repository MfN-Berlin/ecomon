import os
import subprocess
import shutil
import time
import pandas
from io import StringIO
from sqlalchemy import func, text
from datetime import datetime
from celery.utils.log import get_task_logger
from collections import namedtuple
from backend.worker.app import app
from backend.shared.models.db.models import (
    ModelInferenceLogs,
    Models,
    Records,
    ModelInferenceResults,
)

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


BATCH_SIZE = 1000  # Increased from 100 for better throughput


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

    # workerId will be passed to the name of the Docker container where the model runs.
    workerId = job_id

    try:
        # get model string
        model = (
            session.query(
                Models.name,
                Models.additional_docker_arguments,
                Models.additional_model_arguments,
            )
            .filter(Models.id == model_id)
            .first()
        )

        if not model:
            raise Exception(f"Model {model_id} not found")

        # CRITICAL: Optimize session for bulk inserts on heavily indexed partitioned table
        logger.info("Optimizing database session for bulk inserts")
        session.execute(text("SET session_replication_role = replica"))  # Skip FK triggers
        session.execute(text("SET work_mem = '512MB'"))
        session.execute(text("SET maintenance_work_mem = '1GB'"))
        session.execute(text("SET synchronous_commit = OFF"))
        session.execute(text("SET commit_delay = 100000"))
        session.execute(text("SET commit_siblings = 5"))
        session.commit()

        # detach model from session
        ModelData = namedtuple(
            "ModelData",
            ["name", "additional_docker_arguments", "additional_model_arguments"],
        )
        model = ModelData(*model)
        file_counter = 0
        # Get current user and group IDs to make the docker output files readable
        uid = os.getuid()
        gid = os.getgid()

        logger.info(f"Fetching records for site {site_id} and model {model_id}")
        total_count = (
            session.query(func.count(Records.id))
            .join(
                ModelInferenceLogs,
                (Records.id == ModelInferenceLogs.record_id)
                & (ModelInferenceLogs.model_id == model_id),
                isouter=True,
            )
            .filter(Records.site_id == site_id, ModelInferenceLogs.id.is_(None))
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
            session.autoflush = False
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
            docker_volumes = [
                f"-v {host_input_paths_file}:/app/inputPaths.txt",
                f"-v {host_model_output_dir}:/output",
                f"-v {settings.host_base_data_directory}:/data",
            ]
            # Build command as array for better readability and spacing control
            logger.info(f"settings.use_gpu: {settings.use_gpu}")
            command_parts = [
                "docker run",
                "-v /var/run/docker.sock:/var/run/docker.sock",  # needed for docker in docker
                "--rm",  # remove the container after running
                *docker_volumes,
                *(
                    [model.additional_docker_arguments]  # additional docker arguments
                    if model.additional_docker_arguments
                    else []
                ),
                "ghcr.io/mfn-berlin/birdid-model-zoo:latest",
                # "model", # for local testing
                *(
                    [model.additional_model_arguments]
                    if model.additional_model_arguments
                    else []
                ),  # additional models arguments
                f"-i /app/inputPaths.txt",
                f"-m {model.name}",
                f"-o /output",
                f"-ov {host_model_output_dir}",
                "--removeTemporaryResultFile",
                f"-chown {uid}:{gid}",
                "--f pkl",
                *(
                    [f"--gpuIx {settings.use_gpu}"]
                    if settings.use_gpu.lower() != "none"
                    else []
                ),  # gpu
                f"-w {workerId}",
                "-on output",
            ]

            command = " ".join(command_parts)

            logger.info(f"Running command: {command}")

            try:
                process = subprocess.run(
                    command, shell=True, check=True, capture_output=True, text=True
                )
                logger.info(f"Command output: {process.stdout}")
                if process.stderr:
                    logger.warning(f"Command stderr: {process.stderr}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Command failed with exit code {e.returncode}")
                logger.error(f"Command stderr: {e.stderr}")
                raise Exception(f"Docker command failed: {e.stderr}")

            # read the output.pkl file and add the results to the database
            df = pandas.read_pickle(os.path.join(job_temp_dir, "output.pkl"))
            # if confidence is 0 or below confidence resolution
            df = df[df["confidence"] >= 0.01]
            if len(df) == 0:
                # No results to insert, skip to next batch
                continue

            # Map filename to record_id and add model_id
            df["record_id"] = df["filename"].map(record_name_to_id)
            df["model_id"] = model_id

            # CRITICAL: Sort by record_id for partition efficiency
            # This ensures inserts go to the same partition sequentially,
            # reducing partition switching overhead and improving cache utilization
            df = df.sort_values("record_id")

            # Select and reorder columns for insertion
            df_results = df[["record_id", "model_id", "start_time", "end_time", "confidence", "label_id"]]

            # Use COPY for maximum speed (10-50x faster than INSERT on indexed tables)
            logger.info(f"Inserting {len(df_results)} results using COPY")
            connection = session.connection().connection
            cursor = connection.cursor()

            # Create CSV buffer in memory
            buffer = StringIO()
            df_results.to_csv(buffer, index=False, header=False, sep='\t', na_rep='\\N')
            buffer.seek(0)

            # COPY from buffer to table (bypasses most index overhead)
            cursor.copy_expert(
                """
                COPY model_inference_results
                (record_id, model_id, start_time, end_time, confidence, label_id)
                FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t', NULL '\\N')
                """,
                buffer
            )

            # Insert logs using COPY
            logs_df = pandas.DataFrame({
                "model_id": model_id,
                "record_id": sorted(df["record_id"].unique()),
                "analyzed": True
            })

            logger.info(f"Inserting {len(logs_df)} logs using COPY")
            logs_buffer = StringIO()
            logs_df.to_csv(logs_buffer, index=False, header=False, sep='\t')
            logs_buffer.seek(0)

            cursor.copy_expert(
                """
                COPY model_inference_logs
                (model_id, record_id, analyzed)
                FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')
                """,
                logs_buffer
            )

            session.commit()
            session.close()
            db_session.remove()
            session = db_session()

            # Re-apply session optimizations after reconnecting
            session.execute(text("SET session_replication_role = replica"))
            session.execute(text("SET work_mem = '512MB'"))
            session.execute(text("SET maintenance_work_mem = '1GB'"))
            session.execute(text("SET synchronous_commit = OFF"))
            session.execute(text("SET commit_delay = 100000"))
            session.execute(text("SET commit_siblings = 5"))
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
        # Re-enable normal operation
        try:
            session.execute(text("SET session_replication_role = DEFAULT"))
            session.commit()
        except:
            pass
        # Clean up temp directory only if it exists
        if os.path.exists(job_temp_dir):
            shutil.rmtree(job_temp_dir)

    return {
        "status": "success",
        "message": f"Successfully analyzed {file_counter} records for site {site_id}",
    }