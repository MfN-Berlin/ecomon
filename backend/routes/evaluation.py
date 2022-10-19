from sql.query import (
    get_predictions_with_file_id,
    count_species_over_threshold_in_date_range,
)
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from databases import Database
from fastapi import FastAPI
from math import ceil
from sql.query import add_job, update_job_status, get_job_by_id, update_job_progress
import decimal
from datetime import datetime, timezone
import os
from os import path
import time
from util.tools import species_row_to_name
import xlsxwriter
import asyncio


def write_execl_file(filepath, rows, header):

    workbook = xlsxwriter.Workbook(filepath)

    # The workbook object is then used to add new
    # worksheet via the add_worksheet() method.
    worksheet = workbook.add_worksheet()
    # Iterate over the data and write it out row by row.
    for index, value in enumerate(header):
        worksheet.write(0, index, value[0])
        worksheet.set_column(index, index, len(value[0]))
    for row_index, row in enumerate(rows):
        for col_index, header_val in enumerate(header):
            if header_val[1] is not None:
                worksheet.write(row_index + 1, col_index, row[header_val[1]])
    workbook.close()


class GroupingEnum(str, Enum):
    pear = "pear"
    banana = "banana"


ROUTER_TAG = "evaluation"


class EventResponse(BaseModel):
    predictions_count: int
    species_count: int


class BinSizeRequest(BaseModel):
    collection_name: str
    start_datetime: str
    end_datetime: str
    species: Optional[str] = None
    bin_width: Optional[float] = 0.025
    audio_padding: Optional[int] = 5


class BinSizeResponse(BaseModel):
    job_id: int


def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += decimal.Decimal(step)


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
        root + "/bin-sizes", response_model=BinSizeResponse, tags=[ROUTER_TAG],
    )
    async def get_bin_sizes(request: BinSizeRequest,) -> BinSizeResponse:
        collection_name = request.collection_name
        start_datetime = request.start_datetime
        end_datetime = request.end_datetime
        species = request.species
        bin_width = request.bin_width
        audio_padding = request.audio_padding
        result_directory = os.getenv("BAI_SAMPLE_FILE_DIRECTORY")

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
            create_bin_size_xls(
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

    async def create_bin_size_xls(
        collection_name,
        start_datetime,
        end_datetime,
        species,
        bin_width,
        result_filepath,
        job_id,
    ):
        species_list = [species] if species != None else []
        steps = list(float_range(0, 1, bin_width))
        print(steps)
        steps.reverse()
        print(steps)
        total_steps = len(steps) * len(species_list)
        counter = 0
        result_list = []
        # Create headers for excel file
        header = [
            (">= Threshold", "threshold_min"),
            ("< Threshold", "threshold_max"),
        ]
        for species_id in species_list:
            name = species_row_to_name(species_id)
            header.append(
                (
                    "{} Accumulative".format(name),
                    "{}_predictions_acc".format(species_id),
                )
            )
            header.append(
                ("{} Count".format(name), "{}_predictions_count".format(species_id))
            )
        # Create rows for excel file
        for idx, threshold_min in enumerate(steps):
            print("Get prediction count for ", threshold_min)
            row = {
                "threshold_min": threshold_min,
                "threshold_max": threshold_min + bin_width,
            }
            for species_id in species_list:
                query = count_species_over_threshold_in_date_range(
                    collection_name,
                    species_id,
                    threshold_min,
                    1,
                    datetime.fromisoformat(start_datetime[:-1]).astimezone(
                        timezone.utc
                    ),
                    datetime.fromisoformat(end_datetime[:-1]).astimezone(timezone.utc),
                )
                prediction_count = (await database.fetch_one(query))[0]
                row["{}_predictions_acc".format(species_id)] = prediction_count
                row["{}_predictions_count".format(species_id)] = (
                    prediction_count
                    - result_list[idx - 1]["{}_predictions_acc".format(species_id)]
                    if idx > 0
                    else prediction_count
                )

                counter = counter + 1
                result_list.append(row)
                await database.execute(
                    update_job_progress(job_id, round(counter / total_steps * 100))
                )

        write_execl_file(
            result_filepath, result_list, header,
        )
        await database.execute(update_job_status(job_id, "done"))

