import mariadb
import sys
import os
from sql.query import (
    create_index_for_sql_table,
    drop_index_for_sql_table,
)


def connect_to_db():
    try:
        connection = mariadb.connect(
            user=os.getenv("MDAS_MARIADB_USER"),
            password=os.getenv("MDAS_MARIADB_PASSWORD"),
            host=os.getenv("MDAS_MARIADB_HOST"),
            port=int(os.getenv("MDAS_MARIADB_PORT")),
            database=os.getenv("MDAS_MARIADB_DATABASE"),
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    return connection


class DbWorker:
    def __init__(self, batch_prefix):
        self.batch_prefix = batch_prefix
        self.db_connection = connect_to_db()
        self.db_cursor = self.db_connection.cursor()

    def __reduce_to_known_species_array(self, confidences, index_to_name):
        keys = index_to_name.keys()
        # only mapping to smaller array supported no reordering
        result = []
        for key in keys:

            result.append(confidences[int(key)])
        return result

    def commit(self):
        self.db_connection.commit()

    def rollback(self):
        self.db_connection.rollback()

    def add_index(self, prefix, column):
        self.db_cursor.execute(
            create_index_for_sql_table("{}_predictions".format(prefix), column)
        )
        self.db_connection.commit()

    def drop_index(self, prefix, column):
        self.db_cursor.execute(
            drop_index_for_sql_table("{}_predictions".format(prefix), column)
        )
        self.db_connection.commit()

    #     self.db_connection.fl
