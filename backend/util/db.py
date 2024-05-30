import psycopg2
import sys
import os
from sql.query import (
    create_index_for_sql_table,
    drop_index_for_sql_table,
)
from logging import getLogger

logger = getLogger(__name__)

def connect_to_db():
    try:
        connection = psycopg2.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT")),
            database=os.getenv("POSTGRES_DATABASE"),
        )
    except psycopg2.Error as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)

    return connection

class DbWorker:
    def __init__(self, batch_prefix):
        self.batch_prefix = batch_prefix
        self.db_connection = connect_to_db()
        self.db_cursor = self.db_connection.cursor()

    def __reduce_to_known_species_array(self, confidences, index_to_name):
        keys = index_to_name.keys()
        result = []
        for key in keys:
            result.append(confidences[int(key)])
        return result

    def commit(self):
        self.db_connection.commit()

    def rollback(self):
        self.db_connection.rollback()

    def add_index(self, prefix, column):
        index_name = "{}_{}_idx".format(prefix, column)
        query = create_index_for_sql_table("{}_predictions".format(prefix), column)
        try:
            self.db_cursor.execute(query)
            self.commit()
        except psycopg2.Error as e:
            logger.error(f"Error adding index {index_name}: {e}")
            self.rollback()

    def drop_index(self, prefix, column):
        index_name = "{}_{}_idx".format(prefix, column)
        query = drop_index_for_sql_table("{}_predictions".format(prefix), column)
        try:
            self.db_cursor.execute(query)
            self.commit()
        except psycopg2.Error as e:
            logger.error(f"Error dropping index {index_name}: {e}")
            self.rollback()

    def close(self):
        self.db_cursor.close()
        self.db_connection.close()

# Usage example
if __name__ == "__main__":
    worker = DbWorker("example_batch_prefix")
    worker.add_index("example_prefix", "example_column")
    worker.drop_index("example_prefix", "example_column")
    worker.close()
