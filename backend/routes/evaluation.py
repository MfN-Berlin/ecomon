from sql.query import get_predictions_with_file_id
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from databases import Database
from fastapi import FastAPI
from math import ceil


class GroupingEnum(str, Enum):
    pear = "pear"
    banana = "banana"


class GetQueryRequest(BaseModel):
    species: str
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    threshold: Optional[float] = None
    event_grouping: Optional[str] = None


class GetQueryResponse(BaseModel):
    predictions_count: int
    species_count: int


def router(app: FastAPI, root: str, database: Database):
    @app.get(root + "/{prefix_name}/")
    async def get_evaluation(
        prefix_name: str,
        species: str,
        start_datetime: Optional[str] = None,
        end_datetime: Optional[str] = None,
        threshold: Optional[float] = None,
        event_grouping: Optional[str] = None,
    ) -> GetQueryResponse:
        sql_query = get_predictions_with_file_id(
            prefix_name,
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
