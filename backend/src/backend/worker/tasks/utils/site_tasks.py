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
    while not lock_acquired:
        with get_site_data_report_lock(site_id) as acquired:
            if acquired:
                lock_acquired = True
                logger.info(f"Lock acquired for site {site_id}")
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

            else:
                logger.info(f"Waiting for lock to be released for site {site_id}")
                sleep(0.5)
