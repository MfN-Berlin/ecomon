from sqlite3 import DatabaseError
from schemas.route_types import Message
from typing import List, Tuple
from fastapi import APIRouter
from logging import getLogger
from os import getenv
from datetime import datetime, timezone
from asyncio import ensure_future

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
from schemas.route_types import (
    QueryResponse,
    JobId,
    PredictionMax,
    QueryRequest,
)
logger = getLogger(__name__)
root_path = getenv("ROOT_PATH")
from db import database
router = APIRouter()

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


@router.get(
    "/{prefix_name}/predictions/count",
    response_model=int,
    operation_id="getCollectionPredictionsCount",
)
async def get_prefix_predictions_count(prefix_name: str) -> int:
    query = count_predictions(prefix_name)
    # logger.debug(query)
    return (await database.fetch_one(query))[0]

# route to add index to prediction table
@router.put(
    "/{prefix_name}/predictions/{column_name}/index",
    response_model=JobId,
    operation_id="addIndexToCollection",
)
async def add_index_to_prefix(prefix_name: str, column_name: str):
    # TODO: query parameter sanity check
    job_id = await database.execute(
        add_job(
            prefix_name,
            "add_index",
            "pending",
            {"column_name": column_name},
        )
    )
    logger.debug(f"Job {job_id} added to queue")
    
    ensure_future(do_add_index_job(database, job_id, prefix_name, column_name))
    return {"job_id": job_id}

# route to drop index from prediction table
@router.delete(
    "/{prefix_name}/predictions/{column_name}/index",
    response_model=Message,
    operation_id="dropIndexFromCollection",
)
async def drop_index_from_prefix(prefix_name: str, column_name: str):
    sql = drop_index_for_sql_table(f"{prefix_name}_predictions", column_name)
    logger.debug(sql)
    await database.execute(
       sql
    )
    return {"message": "index dropped"}

# route to query prediction table
@router.post(
    "/{prefix_name}/predictions",
    response_model=QueryResponse,
    operation_id="queryCollectionMetadata",
)
async def query_prediction_table(
    prefix_name: str, request: QueryRequest
) -> QueryResponse:
    logger.debug(request)
    query = count_predictions_in_date_range(
        prefix_name,
        datetime.fromisoformat(request.start_datetime[:-1]).replace(
            tzinfo=timezone.utc
        ),
        datetime.fromisoformat(request.end_datetime[:-1]).replace(
            tzinfo=timezone.utc
        ),
    )
    # logger.debug(query)

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

    # logger.debug(query)
    species_count = (await database.fetch_one(query))[0]
    # logger.debug(species_count)
    return QueryResponse(
        predictions_count=predictions_count, species_count=species_count
    )

# route getteing prediction max
@router.get(
    "/{prefix_name}/predictions/max/{species}",
    response_model=List[PredictionMax],
    operation_id="getCollectionPredictionsSpeciesMax",
)
async def get_collection_predictions_species_max(
    prefix_name: str, species: str
) -> List[PredictionMax]:
    query = f"Select record_id, record_datetime, {species} as value from {prefix_name.lower()}_predictions_max order by record_datetime asc"
    try:
        result = await database.fetch_all(query)
        logger.debug("Request done for {}".format(species))
        return [
            PredictionMax(
                record_id=row["record_id"],
                record_datetime=row["record_datetime"],
                value=row["value"],
            )
            for row in result
        ]
    except DatabaseError:
        return []

# Define the response model

@router.get(
    "/{collection_name}/predictions/histogram/{species}",
    response_model=List[int],
    operation_id="getCollectionPredictionsSpeciesHistogram",
)
async def get_species_histogram(collection_name: str, species: str):
    query = f"""
        SELECT * FROM {collection_name.lower()}_species_histogram
        WHERE species = :species

    """
    result = await database.fetch_one(query=query, values={"species": species})

    if result is None:
        return []
    else:
        bins = list(result[2:])

    return bins
