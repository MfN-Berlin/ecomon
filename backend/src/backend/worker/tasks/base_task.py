from backend.worker.services.job_service import JobService
from celery import states
from backend.worker.database import db_session
from backend.worker.app import app
import time


class BaseTask(app.Task):
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()
        super().after_return(status, retval, task_id, args, kwargs, einfo)

    def check_revoked(self):
        if self.request.id:
            result = app.AsyncResult(self.request.id)

            if result.state == states.PENDING:
                self.update_state(state=states.REVOKED)
                time.sleep(1)
                return True
        return False
