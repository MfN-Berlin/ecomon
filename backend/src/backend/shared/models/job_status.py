from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    PREPARING = "preparing"
    FINALIZING = "finalizing"
