import datetime
import json
import os
from routes.route_types import LastUpdate, Message, ResultJob
from sql.query import (
    delete_job,
    get_all_jobs as get_all_jobs_query,
    get_job_by_id,
    delete_job as delete_job_query,
    get_max_updated_at_from_jobs,
)

from typing import List, Optional, Union


def router(app, root, database):
    @app.delete(root + "/{id}", response_model=Message)
    async def delete_job(id: int):
        # get job and check in metadata for filepath
        job = await database.fetch_one(get_job_by_id(id))
        if job is None:
            return None
        else:
            # check if it is type create_sample
            if job[3] == "create_sample":
                # delete file
                result_directory = os.getenv("MDAS_SAMPLE_FILE_DIRECTORY")
                metadata = json.loads(job[4])
                # print(metadata)
                result_directory = os.getenv("MDAS_SAMPLE_FILE_DIRECTORY")
                result_filepath = os.path.join(result_directory, metadata["filename"])
                # print(result_filepath)
                if os.path.exists(result_filepath):
                    os.remove(result_filepath)

            await database.execute(delete_job_query(id))
            return {"message": "job deleted"}

    @app.get(root + "/last_update", response_model=LastUpdate)
    async def get_last_update():
        job = await database.fetch_one(get_max_updated_at_from_jobs())
        return {"last_update": job[0]}

    @app.get(root, response_model=List[ResultJob])
    async def get_all_jobs(
        prefix: Union[str, None] = None,
        type: Union[str, None] = None,
        status: Union[str, None] = None,
    ) -> List[ResultJob]:
        jobs = await database.fetch_all(
            get_all_jobs_query(prefix=prefix, type=type, status=status)
        )
        result = []
        for job in jobs:
            result.append(
                {
                    "id": job[0],
                    "collection": job[1],
                    "type": job[3],
                    "status": job[2],
                    "metadata": json.loads(job[4]),
                    "progress": job[5],
                    "error": job[6],
                    "created_at": job[7],
                    "updated_at": job[8],
                }
            )

        return result
