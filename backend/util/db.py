from telnetlib import NOP
import mariadb
import sys
import os
from sql.insert import insert_prediction, insert_record
from sql.query import (
    create_index_for_sql_table,
    drop_index_for_sql_table,
    get_record_id_by_filepath,
)

import sql.initial as queries


def __create_species__array(index_to_name):
    items = index_to_name.items()
    species = [""] * len(items)
    for key, value in items:
        species[int(key)] = value.lower().replace(" ", "_")
    return species


def connect_to_db():
    try:
        connection = mariadb.connect(
            user=os.getenv("BAI_MARIADB_USER"),
            password=os.getenv("BAI_MARIADB_PASSWORD"),
            host=os.getenv("BAI_MARIADB_HOST"),
            port=int(os.getenv("BAI_MARIADB_PORT")),
            database=os.getenv("BAI_MARIADB_DATABASE"),
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    return connection


def init_db(batch_prefix, index_to_name):
    db_connection = connect_to_db()
    db_cursor = db_connection.cursor()
    records_exists = False
    predictions_exists = False
    records_count = 0
    predictions_count = 0

    species = __create_species__array(index_to_name)

    try:
        records_count = db_cursor.execute(
            queries.check_record_table_exists(batch_prefix)
        )
        records_exists = True
        print(
            "{}_records Table already exists with entries {}".format(
                batch_prefix, records_count
            )
        )
    except mariadb.Error:
        NOP
    try:
        predictions_count = db_cursor.execute(
            queries.check_record_predictions_exists(batch_prefix)
        )
        predictions_exists = True
        print(
            "{}_records Table already exists with entries {}".format(
                batch_prefix, predictions_count
            )
        )
    except mariadb.Error:
        pass

    if records_exists or predictions_exists:
        line = ""
        # while line != "y":
        #     line = input("Tables already exists do you want to resume analysis? (y/n):")
        #     if line == "n":
        #         sys.exit(1)

    if not records_exists:
        print("Create {}_records table".format(batch_prefix))
        db_cursor.execute(queries.create_record_table(batch_prefix))
        db_connection.commit()
    if not predictions_exists:
        print("Create {}_predictions table".format(batch_prefix))
        query_str = queries.create_predictions_table(batch_prefix, species)
        db_cursor.execute(query_str)
        db_connection.commit()
    db_connection.close()


class DbWorker:
    def __init__(self, batch_prefix):
        self.batch_prefix = batch_prefix
        self.db_connection = connect_to_db()
        self.db_cursor = self.db_connection.cursor()

    def add_file(
        self, filepath, filename, record_datetime, duration, channels, commit=True
    ):

        sql_query = insert_record(
            self.batch_prefix, filepath, filename, record_datetime, duration, channels
        )

        self.db_cursor.execute(sql_query)
        if commit:
            self.db_connection.commit()
        sql_query = get_record_id_by_filepath(self.batch_prefix, filepath)
        self.db_cursor.execute(sql_query)
        for i in self.db_cursor:
            return i[0]

    def add_prediction(self, record_id, start, stop, channel, predictions, commit=True):
        sql_query = insert_prediction(
            self.batch_prefix, record_id, start, stop, channel, predictions
        )
        self.db_cursor.execute(sql_query)
        if commit:
            self.db_connection.commit()

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
