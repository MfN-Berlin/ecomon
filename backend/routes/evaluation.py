import asyncio
import os
import time
from routes.route_types import (
    BinSizeRequest,
    Collection,
    DailyHistogramRequest,
    EventResponse,
    JobCreatedResponse,
    PredictionsRequest,
    Report,
    Species,
)
from sql.query import get_predictions_with_file_id
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Union
from databases import Database
from fastapi import FastAPI
from math import ceil
from sql.query import add_job
from os import path

from tasks.create_histogram import create_histogram
from tasks.create_predictions import create_predictions
from tasks.create_daily_histograms import create_daily_histograms


class GroupingEnum(str, Enum):
    pear = "pear"
    banana = "banana"


ROUTER_TAG = "evaluation"


def router(app: FastAPI, root: str, database: Database):
    @app.get(
        root + "/{collection_name}/events",
        response_model=EventResponse,
        tags=[ROUTER_TAG],
    )
    async def get_events(
        collection_name: str,
        species: str,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
        threshold: Optional[float] = None,
        event_grouping: Optional[str] = None,
        audio_padding: Optional[int] = 5,
    ) -> EventResponse:
        sql_query = get_predictions_with_file_id(
            collection_name,
            species,
            threshold,
            audio_padding=None,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        entries = await database.fetch_all(sql_query)
        record_map = {}
        for entry in entries:
            if entry[0] in record_map:
                record_map[entry[0]].append(entry)
            else:
                record_map[entry[0]] = [entry]
        result_map = {}
        for record_id, predictions in record_map.items():
            #       0       1         2           3           4         5         6        7        8
            # (record_id, filepath, datetime, Start_in_s, end_in_s, duration, 'ch_max', threshold, filename)

            # array of minutes by duration
            events_in_minute = [0] * ceil(predictions[0][5] / 60)
            for prediction in predictions:
                # group by event start ins minute x
                events_in_minute[int(prediction[3] / 60)] = 1
            result_map[record_id] = {
                "record_id": record_id,
                "filepath": predictions[0][8],
                "events_in_minute": events_in_minute,
                "events_per_minute": sum(events_in_minute),
            }
        return result_map

    @app.post(
        root + "/bin-sizes", response_model=JobCreatedResponse, tags=[ROUTER_TAG],
    )
    async def get_bin_sizes(request: BinSizeRequest,) -> JobCreatedResponse:
        collection_name = request.collection_name
        start_datetime = request.start_datetime
        end_datetime = request.end_datetime
        species = request.species
        bin_width = request.bin_width
        audio_padding = request.audio_padding
        result_directory = os.getenv("MDAS_SAMPLE_FILE_DIRECTORY")

        if not path.exists(result_directory):
            os.makedirs(result_directory)
        result_filename = "{time}_bin_sizes_{collection_name}_{species}_from_{from_date}_until_{until}_padding_{padding}.xls".format(
            time=round(time.time() * 1000),
            collection_name=collection_name,
            species=species if species != None else "all",
            from_date=start_datetime,
            until=end_datetime,
            padding=audio_padding,
        )
        result_filepath = os.path.join(result_directory, result_filename,)
        job_id = await database.execute(
            add_job(
                collection_name,
                "calc_bin_sizes",
                "running",
                {
                    "filename": result_filename,
                    "filepath": result_filepath,
                    "collection": collection_name,
                    "bin_width": bin_width,
                    "species": species if species != None else "all",
                    "from": start_datetime,
                    "until": end_datetime,
                    "padding": audio_padding,
                },
            )
        )
        asyncio.create_task(
            create_histogram(
                database,
                collection_name,
                start_datetime,
                end_datetime,
                species,
                bin_width,
                result_filepath,
                job_id,
            )
        )

        return {"job_id": job_id}

    @app.post(
        root + "/predictions", response_model=JobCreatedResponse, tags=[ROUTER_TAG],
    )
    async def get_predictions(request: PredictionsRequest,) -> JobCreatedResponse:
        collection_name = request.collection_name
        start_datetime = request.start_datetime
        end_datetime = request.end_datetime
        species = request.species
        audio_padding = request.audio_padding
        request_timezone = request.request_timezone
        min_threshold = request.min_threshold
        max_threshold = request.max_threshold
        result_directory = os.getenv("MDAS_SAMPLE_FILE_DIRECTORY")

        if not path.exists(result_directory):
            os.makedirs(result_directory)
        result_filename = "{time}_predictions_{collection_name}_{species}_from_{from_date}_until_{until}_padding_{padding}.xls".format(
            time=round(time.time() * 1000),
            collection_name=collection_name,
            species=species if species != None else "all",
            from_date=start_datetime,
            until=end_datetime,
            padding=audio_padding,
        )
        result_filepath = os.path.join(result_directory, result_filename,)
        job_id = await database.execute(
            add_job(
                collection_name,
                "calc_predictions",
                "running",
                {
                    "filename": result_filename,
                    "filepath": result_filepath,
                    "collection": collection_name,
                    "species": species if species != None else "all",
                    "from": start_datetime,
                    "until": end_datetime,
                    "padding": audio_padding,
                    "request_timezone": request_timezone,
                    "min_threshold": min_threshold,
                    "max_threshold": max_threshold,
                },
            )
        )
        asyncio.create_task(
            create_predictions(
                database,
                collection_name,
                start_datetime,
                end_datetime,
                species,
                result_filepath,
                job_id,
                request_timezone=request_timezone,
                min_threshold=min_threshold,
                max_threshold=max_threshold,
            )
        )

        return {"job_id": job_id}

    @app.post(
        root + "/daily-histograms",
        response_model=JobCreatedResponse,
        tags=[ROUTER_TAG],
    )
    async def get_daily_histograms(
        request: DailyHistogramRequest,
    ) -> JobCreatedResponse:
        collection_name = request.collection_name
        start_datetime = request.start_datetime
        end_datetime = request.end_datetime
        species = request.species
        bin_width = request.bin_width
        audio_padding = request.audio_padding
        request_timezone = request.request_timezone
        min_threshold = request.min_threshold
        max_threshold = request.max_threshold
        result_directory = os.getenv("MDAS_SAMPLE_FILE_DIRECTORY")

        if not path.exists(result_directory):
            os.makedirs(result_directory)
        result_filename = "{time}_daily_histograms_{collection_name}_{species}_from_{from_date}_until_{until}_padding_{padding}.xls".format(
            time=round(time.time() * 1000),
            collection_name=collection_name,
            species=species if species != None else "all",
            from_date=start_datetime,
            until=end_datetime,
            padding=audio_padding,
        )
        result_filepath = os.path.join(result_directory, result_filename,)

        job_id = await database.execute(
            add_job(
                collection_name,
                "calc_daily_histograms",
                "running",
                {
                    "filename": result_filename,
                    "filepath": result_filepath,
                    "collection": collection_name,
                    "species": species if species != None else "all",
                    "from": start_datetime,
                    "until": end_datetime,
                    "padding": audio_padding,
                    "request_timezone": request_timezone,
                    "min_threshold": min_threshold,
                    "max_threshold": max_threshold,
                },
            )
        )
        asyncio.create_task(
            create_daily_histograms(
                database,
                collection_name,
                start_datetime,
                end_datetime,
                species,
                bin_width,
                result_filepath,
                job_id,
                request_timezone=request_timezone,
                min_threshold=min_threshold,
                max_threshold=max_threshold,
            )
        )

        return {"job_id": job_id}

