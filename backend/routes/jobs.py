import json
from sql.query import get_all_jobs as get_all_jobs_query
from pydantic import BaseModel
from typing import List, Optional, Union
from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel

# define class of job
class Job(BaseModel):
    id: int
    prefix_name: str
    job_type: str
    job_status: str
    metadata: str


def router(app, root, database):
    @app.get(root + "/")
    async def get_all_jobs(
        prefix: Union[str, None] = None,
        type: Union[str, None] = None,
        status: Union[str, None] = None,
    ) -> List[Job]:
        jobs = await database.fetch_all(
            get_all_jobs_query(prefix=prefix, type=type, status=status)
        )
        result = []
        for job in jobs:
            result.append(
                {
                    "id": job[0],
                    "prefix_name": job[1],
                    "job_type": job[2],
                    "job_status": job[3],
                    "metadata": json.loads(job[4]),
                }
            )

        return result

