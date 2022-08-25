from sql.query import (

)
from pydantic import BaseModel
from typing import List, Optional

def router(app, root, database):
   @app.get(root + "/")
   async def get_all_jobs(prefix_name: str, column_name: str):
         result = await database.fetch_all(
            get_column_names_of_sql_table_query("{}_predictions".format(prefix_name))
         )
         species = []
         for i in result:
            column = i[0]
            if column in NON_SPECIES_COLUMN:
                  continue
            species.append(column)
         return species