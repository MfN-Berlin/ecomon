from sql.query import (
    count_entries_in_sql_table,
    sum_values_of_sql_table_column,
    get_datetime_of_first_record_in_sql_table,
    get_datetime_of_last_record_in_sql_table,
)

from pydantic import BaseModel
from datetime import datetime, timezone


class Record(BaseModel):
    id: int
    filepath: str
    filename: str
    record_datetime: datetime
    duration: float
    channels: int


def router(app, root, database):
    @app.get(root + "/{prefix_name}/records/first")
    async def get_first_record_of_prefix(prefix_name: str) -> Record:
        result = await database.fetch_one(
            get_datetime_of_first_record_in_sql_table("{}_records".format(prefix_name))
        )
        # transform datetime to what it is utc timestamp
        record_datetime = result[3].replace(tzinfo=timezone.utc)
        return Record(
            id=result[0],
            filepath=result[1],
            filename=result[2],
            record_datetime=record_datetime.isoformat(),
            duration=result[4],
            channels=result[5],
        )

    @app.get(root + "/{prefix_name}/records/last")
    async def get_last_record_of_prefix(prefix_name: str) -> Record:
        result = await database.fetch_one(
            get_datetime_of_last_record_in_sql_table("{}_records".format(prefix_name))
        )
        # transform datetime to what it is utc timestamp
        record_datetime = result[3].replace(tzinfo=timezone.utc)
        return Record(
            id=result[0],
            filepath=result[1],
            filename=result[2],
            record_datetime=record_datetime.isoformat(),
            duration=result[4],
            channels=result[5],
        )

    @app.get(root + "/{prefix_name}/records/count")
    async def get_prefix_records_count(prefix_name: str) -> int:
        return (
            await database.fetch_one(
                count_entries_in_sql_table("{}_records".format(prefix_name))
            )
        )[0]

    @app.get(root + "/{prefix_name}/records/duration")
    async def get_prefix_records_duration(prefix_name: str) -> float:
        return (
            await (
                database.fetch_one(
                    sum_values_of_sql_table_column(
                        "{}_records".format(prefix_name), "duration"
                    )
                )
            )
        )[0]

