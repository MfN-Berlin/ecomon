from sqlite3 import DatabaseError
from routes.route_types import Message
from sql.query import (
    add_job,
    count_predictions,
    create_index_for_sql_table,
    drop_index_for_sql_table,
    count_entries_in_sql_table,
    count_predictions_in_date_range,
    count_species_over_threshold_in_date_range,
    update_job_failed,
    update_job_status,
)
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
from asyncio import ensure_future


class QueryRequest(BaseModel):
    species: str
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None


class QueryResponse(BaseModel):
    predictions_count: int
    species_count: int


class JobId(BaseModel):
    job_id: int = None


async def do_add_index_job(database, job_id, prefix_name, column_name):
    try:

        await database.execute(
            create_index_for_sql_table(
                "{}_predictions".format(prefix_name), column_name
            )
        )

        await database.execute(update_job_status(job_id, "done"))
    except Exception as e:
        await database.execute(update_job_failed(job_id, str(e)))

    return


def router(app, root, database):
    @app.get(
        root + "/{prefix_name}/predictions/count",
        response_model=int,
        operation_id="getCollectionPredictionsCount",
    )
    async def get_prefix_predictions_count(prefix_name: str) -> int:
        query = count_predictions(prefix_name)
        # print(query)
        return (await database.fetch_one(query))[0]

    # route to add index to prediction table
    @app.put(
        root + "/{prefix_name}/predictions/{column_name}/index",
        response_model=JobId,
        operation_id="addIndexToCollection",
    )
    async def add_index_to_prefix(prefix_name: str, column_name: str):
        # TODO: query parameter sanity check
        job_id = await database.execute(
            add_job(prefix_name, "add_index", "pending", {"column_name": column_name},)
        )
        ensure_future(do_add_index_job(database, job_id, prefix_name, column_name))
        return {"job_id": job_id}

    # route to drop index from prediction table
    @app.delete(
        root + "/{prefix_name}/predictions/{column_name}/index",
        response_model=Message,
        operation_id="dropIndexFromCollection",
    )
    async def drop_index_from_prefix(prefix_name: str, column_name: str):
        await database.execute(
            drop_index_for_sql_table("{}_predictions".format(prefix_name), column_name)
        )
        return {"message": "index dropped"}

    # route to query prediction table
    @app.post(
        root + "/{prefix_name}/predictions",
        response_model=QueryResponse,
        operation_id="queryCollectionMetadata",
    )
    async def query_prediction_table(
        prefix_name: str, request: QueryRequest
    ) -> QueryResponse:
        print(request)
        query = count_predictions_in_date_range(
            prefix_name,
            datetime.fromisoformat(request.start_datetime[:-1]).replace(
                tzinfo=timezone.utc
            ),
            datetime.fromisoformat(request.end_datetime[:-1]).replace(
                tzinfo=timezone.utc
            ),
        )
        # print(query)

        predictions_count = (await database.fetch_one(query))[0]
        query = count_species_over_threshold_in_date_range(
            prefix_name,
            request.species,
            request.threshold_min,
            request.threshold_max,
            datetime.fromisoformat(request.start_datetime[:-1]).replace(
                tzinfo=timezone.utc
            ),
            datetime.fromisoformat(request.end_datetime[:-1]).replace(
                tzinfo=timezone.utc
            ),
        )

        # print(query)
        species_count = (await database.fetch_one(query))[0]
        # print(species_count)
        return QueryResponse(
            predictions_count=predictions_count, species_count=species_count
        )

    # rou

