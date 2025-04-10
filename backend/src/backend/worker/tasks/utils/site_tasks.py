from logging import Logger
from time import sleep
from requests import Session
from backend.worker.services.job_service import JobService
from backend.worker.tasks.utils.lock_service import get_site_data_report_lock
from backend.shared.consts import task_topic
from backend.worker.services.task_creator import TaskCreator


def wait_for_lock_and_create_report(
    request_id: str, site_id: int, session: Session, logger: Logger
):
    lock_acquired = False
    logger.info(f"Waiting for lock for site {site_id}")
    while not lock_acquired:
        try:
            with get_site_data_report_lock(site_id, timeout=10) as acquired:
                if acquired:
                    lock_acquired = True
                    logger.info(f"Lock acquired for site {site_id}")
                    try:

                        if not JobService.does_other_site_job_exists(
                            session,
                            request_id,
                            [
                                task_topic.SCAN_DIRECTORIES.value,
                                task_topic.CREATE_SITE_DATA_REPORT.value,
                            ],
                            site_id,
                        ):
                            logger.info(
                                f"No More tasks are still running for site {site_id}, start create report task"
                            )

                            TaskCreator.create_site_data_report_task(session, site_id)

                    except Exception as e:
                        # Log the error but ensure the lock is released by letting the context manager exit
                        logger.error(f"Error while processing site {site_id}: {str(e)}")
                        raise  # Re-raise the exception after logging
                else:
                    logger.info(f"Waiting for lock to be released for site {site_id}")
                    sleep(0.5)
        except Exception as e:
            # Handle any exceptions that might occur with the lock itself
            logger.error(f"Error with lock for site {site_id}: {str(e)}")
            # Wait a bit before retrying to avoid tight loop in case of persistent errors
            sleep(1)
