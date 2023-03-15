import json
import os
from fastapi import HTTPException
from routes.route_types import Collection, Report, Species
from sql.query import (
    count_entries_in_sql_table,
    get_datetime_of_first_record_in_sql_table,
    get_column_names_of_sql_table_query,
    get_all_prediction_table_names,
    get_index_names_of_sql_table_ending_with,
)

from typing import List


NON_SPECIES_COLUMN = ["id", "record_id", "start_time", "end_time", "channel"]


def remove_substring_from_end(string: str, substring: str):
    return string[: -len(substring)]


def router(app, root, database):
    @app.get(root + "/list", response_model=List[str])
    async def read_prefix():
        result = await database.fetch_all(get_all_prediction_table_names())
        return [remove_substring_from_end(i[0], "_predictions") for i in result]

    @app.get(root + "/{prefix_name}", response_model=Collection)
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

    @app.get(root + "/{prefix_name}/species", response_model=List[Species])
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

    @app.get(root + "/{collection_name}/report", response_model=Report)
    async def get_collection_report(collection_name: str) -> Report:
        # read env variable for report path

        filename = f"{collection_name}_report.json"
        reports_directory = os.getenv("MDAS_REPORTS_DIRECTORY")
        if reports_directory == None:
            raise Exception("MDAS_REPORTS_DIRECTORY not set")
        file_path = os.path.join(reports_directory, filename)
        try:
            with open(file_path) as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            raise HTTPException(
                status_code=404, detail=f"File {filename}.json not found"
            )

