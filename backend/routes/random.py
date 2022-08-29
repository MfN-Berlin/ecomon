import asyncio
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
import os
from os import path
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import FileResponse
from routes.predictions import do_add_index_job
from sql.query import add_job, update_job_status

from create_sample import create_sample


class Record(BaseModel):
    id: int
    filepath: str
    filename: str
    record_datetime: datetime
    duration: float
    channels: int


class RandomSampleRequest(BaseModel):
    species: str
    sample_size: int
    audio_padding: Optional[int] = None
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    threshold: Optional[float] = None


sample_executor = ThreadPoolExecutor(10)


def router(app, root, database):

    # route to get random sample from prediction table
    @app.get("/random_sample")
    async def get_random_sample(
        prefix: str,
        species: str,
        threshold: float,
        sample_size: int = 10,
        audio_padding: int = 0,
        start_datetime: str = None,
        end_datetime: str = None,
    ):
        # syncronus function in thread for asyncio compatibility
        BAI_TMP_DIRECTORY = os.getenv("BAI_TMP_DIRECTORY")
        if not path.exists(BAI_TMP_DIRECTORY):
            os.makedirs(BAI_TMP_DIRECTORY)

        result_directory = os.getenv("BAI_SAMPLE_FILE_DIRECTORY")
        if not path.exists(result_directory):
            os.makedirs(result_directory)
        result_filename = "{prefix}_{species}_lq_{threshold}_from_{from_date}_until_{until}_samples_{samples}_padding_{padding}.zip".format(
            prefix=prefix,
            species=species,
            threshold=threshold,
            from_date=start_datetime,
            until=end_datetime,
            samples=sample_size,
            padding=audio_padding,
        )
        result_filepath = os.path.join(result_directory, result_filename,)

        def func():

            create_sample(
                prefix=prefix,
                result_filepath=result_filepath,
                BAI_TMP_DIRECTORY=BAI_TMP_DIRECTORY,
                species=species,
                threshold=threshold,
                sample_size=sample_size,
                audio_padding=audio_padding,
                start_datetime=datetime.fromisoformat(start_datetime[:-1]).astimezone(
                    timezone.utc
                ),
                end_datetime=datetime.fromisoformat(end_datetime[:-1]).astimezone(
                    timezone.utc
                ),
            )

        async def task(database, job_id):
            loop = asyncio.get_event_loop()
            await database.execute(update_job_status(job_id, "running"))
            await loop.run_in_executor(sample_executor, func)
            await database.execute(update_job_status(job_id, "done"))

        job_id = await database.execute(
            add_job(
                prefix,
                "create_sample",
                "pending",
                {
                    "filename": result_filename,
                    "filepath": result_filepath,
                    "prefix": prefix,
                    "species": species,
                    "threshold": threshold,
                    "from_date": start_datetime,
                    "until": end_datetime,
                    "samples": sample_size,
                    "padding": audio_padding,
                },
            )
        )
        asyncio.ensure_future(task(database, job_id))
        return {"job_id": job_id}
        # return file stream

        # return FileResponse(
        #     result_filepath, media_type="application/zip", filename=result_filename
        # )
