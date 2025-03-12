# backend/worker/services/lock_service.py

import redis
from contextlib import contextmanager
from backend.worker.settings import WorkerSettings

settings = WorkerSettings()

# Initialize Redis client
redis_client = redis.StrictRedis(
    host=settings.redis_host, port=settings.redis_port, db=0
)


@contextmanager
def distributed_lock(lock_name, timeout=10):
    lock = redis_client.lock(lock_name, timeout=timeout)
    acquired = lock.acquire(blocking=True)
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()


def get_site_data_report_lock(site_id: int):
    return redis_client.lock(f"create_site_data_report_lock_{site_id}", timeout=10)
