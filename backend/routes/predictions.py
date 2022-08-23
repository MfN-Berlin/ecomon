from sql.query import (
    create_index_for_sql_table,
    drop_index_for_sql_table,
    count_entries_in_sql_table,
    count_predictions_in_date_range,
    count_species_over_threshold_in_date_range,
)
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional


class QueryRequest(BaseModel):
    species: str
    start_datetime: Optional[str] = None
    end_datetime: Optional[str] = None
    threshold: Optional[float] = None


class QueryResponse(BaseModel):
    predictions_count: int
    species_count: int


def router(app, root, database):
    @app.get(root + "/{prefix_name}/predictions/count")
    async def get_prefix_predictions_count(prefix_name: str) -> int:
        return (
            await database.fetch_one(
                count_entries_in_sql_table("{}_predictions".format(prefix_name))
            )
        )[0]

    # route to add index to prediction table
    @app.put(root + "/{prefix_name}/predictions/{column_name}/index")
    async def add_index_to_prefix(prefix_name: str, column_name: str):
        # TODO: query parameter sanity check
        await database.execute(
            create_index_for_sql_table(
                "{}_predictions".format(prefix_name), column_name
            )
        )
        return {"message": "index created"}

    # route to drop index from prediction table
    @app.delete(root + "/{prefix_name}/predictions/{column_name}/index")
    async def drop_index_from_prefix(prefix_name: str, column_name: str):
        await database.execute(
            drop_index_for_sql_table("{}_predictions".format(prefix_name), column_name)
        )
        return {"message": "index dropped"}

    # route to query prediction table
    @app.post(root + "/{prefix_name}/predictions")
    async def query_prediction_table(
        prefix_name: str, request: QueryRequest
    ) -> QueryResponse:
        print(request)
        predictions_count = (
            await database.fetch_one(
                count_predictions_in_date_range(
                    prefix_name,
                    datetime.fromisoformat(request.start_datetime[:-1]).astimezone(
                        timezone.utc
                    ),
                    datetime.fromisoformat(request.end_datetime[:-1]).astimezone(
                        timezone.utc
                    ),
                )
            )
        )[0]

        species_count = (
            await database.fetch_one(
                count_species_over_threshold_in_date_range(
                    prefix_name,
                    request.species,
                    request.threshold,
                    datetime.fromisoformat(request.start_datetime[:-1]).astimezone(
                        timezone.utc
                    ),
                    datetime.fromisoformat(request.end_datetime[:-1]).astimezone(
                        timezone.utc
                    ),
                )
            )
        )[0]
        print(species_count)
        return QueryResponse(
            predictions_count=predictions_count, species_count=species_count
        )

    # rou

