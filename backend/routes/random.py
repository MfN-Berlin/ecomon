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
    prefix: str
    species: str
    sample_size: int
    threshold: float
    audio_padding: Optional[int] = 5
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None


sample_executor = ThreadPoolExecutor(10)


def router(app, root, database):

    # route to get random sample from prediction table
    @app.post("/random_sample")
    async def get_random_sample(request: RandomSampleRequest):
        # syncronus function in thread for asyncio compatibility
        BAI_TMP_DIRECTORY = os.getenv("BAI_TMP_DIRECTORY")
        if not path.exists(BAI_TMP_DIRECTORY):
            os.makedirs(BAI_TMP_DIRECTORY)

        result_directory = os.getenv("BAI_SAMPLE_FILE_DIRECTORY")
        if not path.exists(result_directory):
            os.makedirs(result_directory)
        result_filename = "{prefix}_{species}_lq_{threshold}_from_{from_date}_until_{until}_samples_{samples}_padding_{padding}.zip".format(
            prefix=request.prefix,
            species=request.species,
            threshold=request.threshold,
            from_date=request.start_datetime,
            until=request.end_datetime,
            samples=request.sample_size,
            padding=request.audio_padding,
        )
        result_filepath = os.path.join(result_directory, result_filename,)

        async def task(database, job_id):
            loop = asyncio.get_event_loop()

            def func():
                create_sample(
                    prefix=request.prefix,
                    result_filepath=result_filepath,
                    BAI_TMP_DIRECTORY=BAI_TMP_DIRECTORY,
                    species=request.species,
                    threshold=request.threshold,
                    sample_size=request.sample_size,
                    audio_padding=request.audio_padding,
                    start_datetime=datetime.fromisoformat(
                        request.start_datetime[:-1]
                    ).astimezone(timezone.utc),
                    end_datetime=datetime.fromisoformat(
                        request.end_datetime[:-1]
                    ).astimezone(timezone.utc),
                    job_id=job_id,
                )

            await database.execute(update_job_status(job_id, "running"))
            await loop.run_in_executor(sample_executor, func)
            await database.execute(update_job_status(job_id, "done"))

        job_id = await database.execute(
            add_job(
                request.prefix,
                "create_sample",
                "pending",
                {
                    "filename": result_filename,
                    "filepath": result_filepath,
                    "prefix": request.prefix,
                    "species": request.species,
                    "threshold": request.threshold,
                    "from_date": request.start_datetime,
                    "until": request.end_datetime,
                    "samples": request.sample_size,
                    "padding": request.audio_padding,
                },
            )
        )
        asyncio.ensure_future(task(database, job_id))
        return {"job_id": job_id}
        # return file stream

        # return FileResponse(
        #     result_filepath, media_type="application/zip", filename=result_filename
        # )
