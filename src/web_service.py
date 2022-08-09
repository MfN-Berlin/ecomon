import asyncio
import os
from typing import Union
import databases
import sqlalchemy
from sql.query import (
    create_index_for_sql_table,
    drop_index_for_sql_table,
    get_column_names_of_sql_table_query,
    count_entries_in_sql_table,
    get_index_names_of_sql_table_ending_with,
)


from fastapi import FastAPI
import argparse
from os import path
from dotenv import load_dotenv
from db import connect_to_db
from sql.query import get_prediction_random_sample
from uuid import uuid4
from tools import parse_boolean
from typing import List, Optional
from pydantic import BaseModel
from create_sample import create_sample
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import FileResponse

sample_executor = ThreadPoolExecutor(10)

NON_SPECIES_COLUMN = ["id", "record_id", "start_time", "end_time", "channel"]

load_dotenv()
# initiliaze database connection
user = os.getenv("BAI_MARIADB_USER")
password = os.getenv("BAI_MARIADB_PASSWORD")
host = os.getenv("BAI_MARIADB_HOST")
port = int(os.getenv("BAI_MARIADB_PORT"))
database = os.getenv("BAI_MARIADB_DATABASE")
database_connection_string = "mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4".format(
    user=user, password=password, host=host, port=port, dbname=database
)

database = databases.Database(database_connection_string)


def remove_substring_from_end(string: str, substring: str):
    return string[: -len(substring)]


def get_all_prediction_table_names():
    return """
    SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA = 'bai' and TABLE_NAME like '%_predictions'
    """


# A Pydantic model
class Collection(BaseModel):
    name: str
    species_list: List[str]
    records_count: int
    predictions_count: int
    indicated_species_columns: List[str]


class RandomSampleRequest(BaseModel):
    species: str
    sample_size: int
    audio_padding: Optional[int] = None
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    threshold: Optional[float] = None


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/prefix/list")
async def read_prefix():
    result = await database.fetch_all(get_all_prediction_table_names())
    return [remove_substring_from_end(i[0], "_predictions") for i in result]


@app.get("/prefix/{prefix_name}")
async def get_prefix_informations(prefix_name: str):

    result = await database.fetch_all(
        get_column_names_of_sql_table_query("{}_predictions".format(prefix_name))
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
            count_entries_in_sql_table("{}_records".format(prefix_name))
        )
    )[0]

    # count predictions entries
    predictions_count = (
        await database.fetch_one(
            count_entries_in_sql_table("{}_predictions".format(prefix_name))
        )
    )[0]

    # get indicated species columns
    indicated_species_index = await database.fetch_all(
        get_index_names_of_sql_table_ending_with(
            "{}_predictions".format(prefix_name), "_index"
        )
    )

    indicated_species_columns = [
        remove_substring_from_end(i[0], "_index") for i in indicated_species_index
    ]

    return Collection(
        name=prefix_name,
        species_list=species,
        records_count=records_count,
        predictions_count=predictions_count,
        indicated_species_columns=indicated_species_columns,
    )


# route to add index to prediction table
@app.post("/prefix/{prefix_name}/add_index/{column_name}")
async def add_index_to_prefix(prefix_name: str, column_name: str):
    # TODO: query parameter sanity check

    await database.execute(
        create_index_for_sql_table("{}_predictions".format(prefix_name), column_name)
    )
    return {"message": "index created"}


# route to drop index from prediction table
@app.post("/prefix/{prefix_name}/drop_index/{column_name}")
async def drop_index_from_prefix(prefix_name: str, column_name: str):
    await database.execute(
        drop_index_for_sql_table("{}_predictions".format(prefix_name), column_name)
    )
    return {"message": "index dropped"}


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
    tmp_directory = os.getenv("WEB_SERVICE_TMP_DIRECTORY")
    if not path.exists(tmp_directory):
        os.makedirs(tmp_directory)

    result_directory = os.getenv("WEB_SERVICE_RESULT_DIRECTORY")
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
            tmp_directory=tmp_directory,
            species=species,
            threshold=threshold,
            sample_size=sample_size,
            audio_padding=audio_padding,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(sample_executor, func)
    # return file stream
    return FileResponse(
        result_filepath, media_type="application/zip", filename=result_filename
    )

