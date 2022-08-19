import asyncio
import os
import databases
from sql.query import (
    create_index_for_sql_table,
    drop_index_for_sql_table,
    get_column_names_of_sql_table_query,
    count_entries_in_sql_table,
    get_index_names_of_sql_table_ending_with,
    sum_values_of_sql_table_cloumn,
    count_predictions_in_date_range,
    count_species_over_threshold_in_date_range,
    get_datetime_of_first_record_in_sql_table,
    get_datetime_of_last_record_in_sql_table,
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from os import path
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel
from create_sample import create_sample
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import FileResponse, RedirectResponse
from datetime import datetime

sample_executor = ThreadPoolExecutor(10)

NON_SPECIES_COLUMN = ["id", "record_id", "start_time", "end_time", "channel"]

load_dotenv()

path_prefix = os.getenv("ROOT_PATH")
# initiliaze database connection
user = os.getenv("BAI_MARIADB_USER")

password = os.getenv("BAI_MARIADB_PASSWORD")
host = os.getenv("BAI_MARIADB_HOST")
port = int(os.getenv("BAI_MARIADB_PORT"))
database = os.getenv("BAI_MARIADB_DATABASE")
database_connection_string = "mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4".format(
    user=user, password=password, host=host, port=port, dbname=database
)
print(database_connection_string)
print(user)
print(password)

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


class Species(BaseModel):
    name: str
    has_index: bool


class RandomSampleRequest(BaseModel):
    species: str
    sample_size: int
    audio_padding: Optional[int] = None
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    threshold: Optional[float] = None


class QueryRequest(BaseModel):
    species: str
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    threshold: Optional[float] = None


class QueryResponse(BaseModel):
    predictions_count: int
    species_count: int


class Record(BaseModel):
    id: int
    filepath: str
    filename: str
    record_datetime: datetime
    duration: float
    channels: int


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
def read_root():
    return RedirectResponse(
        "{}/docs".format(path_prefix if path_prefix else ""), status_code=302
    )


@app.get("/prefix/list")
async def read_prefix():
    result = await database.fetch_all(get_all_prediction_table_names())
    return [remove_substring_from_end(i[0], "_predictions") for i in result]


@app.get("/prefix/{prefix_name}")
async def get_prefix_informations(prefix_name: str) -> Collection:

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


@app.get("/prefix/{prefix_name}/species")
async def get_prefix_species(prefix_name: str) -> List[Species]:
    result = await database.fetch_all(
        get_column_names_of_sql_table_query("{}_predictions".format(prefix_name))
    )

    indicated_species_index = await database.fetch_all(
        get_index_names_of_sql_table_ending_with(
            "{}_predictions".format(prefix_name), "_index"
        )
    )

    indicated_species_columns = [
        remove_substring_from_end(i[0], "_index") for i in indicated_species_index
    ]

    species = []
    for i in result:
        column = i[0]
        if column in NON_SPECIES_COLUMN:
            continue
        species.append(
            Species(name=column, has_index=column in indicated_species_columns)
        )

    return species


@app.get("/prefix/{prefix_name}/records/first")
async def get_first_record_of_prefix(prefix_name: str) -> Record:
    result = await database.fetch_one(
        get_datetime_of_first_record_in_sql_table("{}_records".format(prefix_name))
    )
    print(type(result[3]))
    return Record(
        id=result[0],
        filepath=result[1],
        filename=result[2],
        record_datetime=result[3],
        duration=result[4],
        channels=result[5],
    )


@app.get("/prefix/{prefix_name}/records/last")
async def get_last_record_of_prefix(prefix_name: str) -> Record:
    result = await database.fetch_one(
        get_datetime_of_last_record_in_sql_table("{}_records".format(prefix_name))
    )
    print(type(result[3]))
    return Record(
        id=result[0],
        filepath=result[1],
        filename=result[2],
        record_datetime=result[3],
        duration=result[4],
        channels=result[5],
    )


@app.get("/prefix/{prefix_name}/records/count")
async def get_prefix_records_count(prefix_name: str) -> int:
    return (
        await database.fetch_one(
            count_entries_in_sql_table("{}_records".format(prefix_name))
        )
    )[0]


@app.get("/prefix/{prefix_name}/records/duration")
async def get_prefix_records_duration(prefix_name: str) -> float:
    return (
        await (
            database.fetch_one(
                sum_values_of_sql_table_cloumn(
                    "{}_records".format(prefix_name), "duration"
                )
            )
        )
    )[0]


@app.get("/prefix/{prefix_name}/predictions/count")
async def get_prefix_predictions_count(prefix_name: str) -> int:
    return (
        await database.fetch_one(
            count_entries_in_sql_table("{}_predictions".format(prefix_name))
        )
    )[0]


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


# route to query prediction table
@app.post("/prefix/{prefix_name}/predictions")
async def query_prediction_table(
    prefix_name: str, request: QueryRequest
) -> QueryResponse:
    print(request)
    predictions_count = (
        await database.fetch_one(
            count_predictions_in_date_range(
                prefix_name, request.start_datetime, request.end_datetime
            )
        )
    )[0]

    species_count = (
        await database.fetch_one(
            count_species_over_threshold_in_date_range(
                prefix_name,
                request.species,
                request.threshold,
                request.start_datetime,
                request.end_datetime,
            )
        )
    )[0]
    print(species_count)
    return QueryResponse(
        predictions_count=predictions_count, species_count=species_count
    )


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
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(sample_executor, func)
    # return file stream
    return FileResponse(
        result_filepath, media_type="application/zip", filename=result_filename
    )

