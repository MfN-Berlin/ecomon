from sql.query import (
    count_entries_in_sql_table,
    get_datetime_of_first_record_in_sql_table,
    get_column_names_of_sql_table_query,
    get_all_prediction_table_names,
    get_index_names_of_sql_table_ending_with,
)
from pydantic import BaseModel
from typing import List, Optional

NON_SPECIES_COLUMN = ["id", "record_id", "start_time", "end_time", "channel"]


def remove_substring_from_end(string: str, substring: str):
    return string[: -len(substring)]


class Collection(BaseModel):
    name: str
    species_list: List[str]
    records_count: int
    predictions_count: int
    indicated_species_columns: List[str]


class Species(BaseModel):
    name: str
    has_index: bool


def router(app, root, database):
    @app.get(root + "/list")
    async def read_prefix():
        result = await database.fetch_all(get_all_prediction_table_names())
        return [remove_substring_from_end(i[0], "_predictions") for i in result]

    @app.get(root + "/{prefix_name}")
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

    @app.get(root + "/{prefix_name}/species")
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

