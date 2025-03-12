import asyncio
from celery.result import AsyncResult
from celery import states

from fastapi import HTTPException, status

import logging
from logging.config import dictConfig
from backend.api.logger_config import get_log_config


dictConfig(get_log_config(timestamp=True))
logger = logging.getLogger(__name__)


class TaskService:
    async def cancel_task(self, task_id: str):
        """
        Attempt soft cancellation, check every second, fall back to hard cancellation after 30 seconds
        """
        result = AsyncResult(task_id)

        if result.ready():
            return {
                "task_id": task_id,
                "success": True,
                "message": "Task already completed",
            }
        result.revoke()
        result.forget()
        # Check every second for 30 seconds
        for _ in range(50):
            result = AsyncResult(task_id)
            print(result.state)
            
            if result.state == states.REVOKED:
                return {
                    "success": True,
                    "message": "Task was soft cancelled",
                    "task_id": task_id,
                }
            result.forget()
            logger.debug(f"Task {task_id} is still running")
            await asyncio.sleep(0.1)

        return {
            "success": False,
            "message": "Task is still running",
            "task_id": int(task_id),
        }
