import json
import os
from fastapi import HTTPException
from schemas.route_types import Collection, Report, Species
from sql.query import (
    count_entries_in_sql_table,
    get_datetime_of_first_record_in_sql_table,
    get_column_names_of_sql_table_query,
    get_all_prediction_table_names,
    get_index_names_of_sql_table_ending_with,
)

from typing import List
from fastapi import APIRouter
from db import database
from logging import getLogger
logger = getLogger(__name__)
router = APIRouter()

NON_SPECIES_COLUMN = ["id", "record_id", "start_time", "end_time", "channel"]


def remove_substring_from_end(string: str, substring: str):
    return string[: -len(substring)]
def remove_prefix_from_string(string: str, prefix: str):
    return string[len(prefix) :]


@router.get(
    "/list", response_model=List[str], operation_id="getCollectionNames"
)
async def read_prefix():
    result = await database.fetch_all(get_all_prediction_table_names())
    return [remove_substring_from_end(i[0], "_predictions") for i in result]

@router.get(
    "/{prefix_name}",
    response_model=Collection,
    operation_id="getCollectionInformation",
)
async def get_prefix_information(prefix_name: str) -> Collection:

    result = await database.fetch_all(
        get_column_names_of_sql_table_query("{}_predictions".format(prefix_name.lower()))
    )

    species = []
    for i in result:
        column = i[0]
        if column in NON_SPECIES_COLUMN:
            continue
        species.append(column)

    # count records entries
    records_count = (
        await database.fetch_one(
            count_entries_in_sql_table(f"{prefix_name.lower()}_records")
        )
    )[0]

    # count predictions entries
    predictions_count = (
        await database.fetch_one(
            count_entries_in_sql_table("{}_predictions".format(prefix_name.lower()))
        )
    )[0]

    # get indicated species columns
    indicated_species_index = await database.fetch_all(
        get_index_names_of_sql_table_ending_with(
            "{}_predictions".format(prefix_name), "_index"
        )
    )
    logger.debug(indicated_species_index)

    indicated_species_columns = [
        remove_prefix_from_string(remove_substring_from_end(i[0], "_index"),f"predictions_{prefix_name.lower()}_") for i in indicated_species_index
    ]

    return Collection(
        name=prefix_name,
        species_list=species,
        records_count=records_count,
        predictions_count=predictions_count,
        indicated_species_columns=indicated_species_columns,
    )

@router.get(
    "/{prefix_name}/species",
    response_model=List[Species],
    operation_id="getCollectionSpecies",
)
async def get_prefix_species(prefix_name: str) -> List[Species]:
    result = await database.fetch_all(
        get_column_names_of_sql_table_query("{}_predictions".format(prefix_name.lower()))
    )

    indicated_species_index = await database.fetch_all(
        get_index_names_of_sql_table_ending_with(
            "{}_predictions".format(prefix_name), "_index"
        )
    )

    indicated_species_columns = [
        remove_prefix_from_string(remove_substring_from_end(i[0], "_index"),f"predictions_{prefix_name.lower()}_") for i in indicated_species_index
    ]
    logger.debug(indicated_species_columns)

    species = []
    for i in result:
        column = i[0]
        if column in NON_SPECIES_COLUMN:
            continue
        species.append(
            Species(name=column, has_index=column in indicated_species_columns)
        )

    return species

@router.get(
    "/{collection_name}/report",
    response_model=Report,
    operation_id="getCollectionReport",
)
async def get_collection_report(collection_name: str) -> Report:
    # read env variable for report path

    filename = f"{collection_name}_report.json"
    reports_directory = os.getenv("REPORTS_DIRECTORY")
    if reports_directory == None:
        raise Exception("REPORTS_DIRECTORY not set")
    file_path = os.path.join(reports_directory, filename)
    print(f"Reading report from {file_path}")
    try:
        with open(file_path) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"File {filename} not found"
        )

