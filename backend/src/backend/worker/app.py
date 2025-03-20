import logging
import subprocess
import time
from celery import Celery, signals
from celery.signals import task_revoked

from backend.worker.settings import WorkerSettings
from backend.worker.database import get_new_Session, db_session
from backend.worker.services.job_service import JobService

settings = WorkerSettings()
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)

app = Celery(
    "ecomon",
    broker=settings.broker_url,
    backend=settings.backend_url,
    task_ignore_result=False,
    pool="gevent",
    include=[
        "backend.worker.tasks.scan_directories_task",
        "backend.worker.tasks.delete_records_from_site_task",
        "backend.worker.tasks.create_site_data_report_task",
        "backend.worker.tasks.model_inference_site_task",
    ],
)


# Reset unfinished jobs using APP session
def reset_startup_jobs():
    session = db_session()
    try:
        reset_count = JobService.reset_unfinished_jobs(session)
        if reset_count > 0:
            logger.warning(f"Reset {reset_count} unfinished jobs on startup")
        session.commit()
    except Exception as e:
        logger.error(f"Error resetting jobs: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        db_session.remove()


def shutdown_docker_containers():
    """Shutdown all running Docker containers with names starting with 'bmz_' or 'bmzu_'"""
    try:
        # Get all running containers with names starting with 'bmz_' or 'bmzu_'
        cmd_list = ["docker", "ps", "--format", "{{.Names}}"]
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)

        containers = [
            container
            for container in result.stdout.strip().split("\n")
            if container
            and (container.startswith("bmz_") or container.startswith("bmzu_"))
        ]

        if containers:
            logger.warning(
                f"Found {len(containers)} containers to shut down: {containers}"
            )

            # Stop each container
            for container in containers:
                logger.info(f"Stopping container: {container}")
                stop_cmd = ["docker", "stop", container]
                subprocess.run(stop_cmd, check=True)

            logger.warning("All matching containers have been stopped")
            time.sleep(5)  # Wait for birdId zoo containers to stop
        else:
            logger.warning("No matching containers found to shut down")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing Docker command: {str(e)}")
    except Exception as e:
        logger.error(f"Error shutting down Docker containers: {str(e)}")


@signals.celeryd_init.connect
def celery_init_handler(**kwargs):
    """Handler that runs when Celery initializes"""
    logger.info("Celery initializing, performing startup tasks...")
    shutdown_docker_containers()
    reset_startup_jobs()


@signals.task_success.connect
def task_success_handler(sender=None, **kwargs):
    session = get_new_Session()
    try:
        JobService.set_job_done(session, sender.request.id)

        session.commit()
        result = app.AsyncResult(sender.request.id)

        logger.info(f"Task {sender.name} succeeded {result.state} !")
    except Exception as e:
        logger.error(f"Task success error: {str(e)}", exc_info=True)
        session.rollback()
    finally:
        session.close()
        db_session.remove()


@signals.task_failure.connect
def task_failure_handler(sender=None, exception=None, traceback=None, **kwargs):
    session = get_new_Session()
    try:
        JobService.set_job_error(session, sender.request.id, str(exception))
        session.commit()
        logger.error(f"Task {sender.name} failed: {str(exception)}")
    except Exception as e:
        logger.error(f"Task failure handler error: {str(e)}", exc_info=True)
        session.rollback()
    finally:
        session.close()
        db_session.remove()


@signals.task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, **kwargs):
    session = get_new_Session()
    try:
        JobService.set_job_running(session, task_id)
        session.commit()
        logger.info(f"Task {sender.name} started")
    except Exception as e:
        logger.error(f"Task prerun error: {str(e)}")
        session.rollback()
    finally:
        session.close()
        db_session.remove()


@task_revoked.connect
def task_revoked_handler(
    sender=None, terminated=None, signum=None, expired=None, **kwargs
):
    session = get_new_Session()
    try:
        JobService.set_job_done(session, sender.request.id)
        session.commit()
        logger.info(f"Task {sender.name} revoked")
    except Exception as e:
        logger.error(f"Task revoked handler error: {str(e)}")
        session.rollback()
    finally:
        session.close()
        db_session.remove()
