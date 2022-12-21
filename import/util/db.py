from telnetlib import NOP
import mariadb
import sys
import os
from pytz import utc
from sql.insert import insert_prediction, insert_record
from sql.query import (
    create_index_for_sql_table,
    drop_index_for_sql_table,
    get_record_id_by_filepath,
)

import sql.initial as queries


def __create_species__array(index_to_name):
    items = index_to_name.items()
    species = []
    for key, value in items:
        species.append(value.lower().replace(" ", "_"))
    return species


def connect_to_db():
    try:
        print( "Connecting to MariaDB Platform...")
        print("MDAS_MARIADB_USER: {}".format(os.getenv("MDAS_MARIADB_USER")))
        print("MDAS_MARIADB_PASSWORD: {}".format(os.getenv("MDAS_MARIADB_PASSWORD")))
        print("MDAS_MARIADB_HOST: {}".format(os.getenv("MDAS_MARIADB_HOST")))
        print("MDAS_MARIADB_PORT: {}".format(os.getenv("MDAS_MARIADB_PORT")))
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

    def __reduce_to_known_species_array(self, confidences, index_to_name):
        keys = index_to_name.keys()
        # only mapping to smaller array supported no reordering
        result = []
        for key in keys:

            result.append(confidences[int(key)])
        return result

    def add_file(
        self, filepath, filename, record_datetime, duration, channels, commit=True
    ):
        utc_datetime = record_datetime.astimezone(utc)

        sql_query = insert_record(
            self.batch_prefix,
            filepath,
            filename,
            utc_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            duration,
            channels,
        )

        self.db_cursor.execute(sql_query)
        if commit:
            self.db_connection.commit()
        sql_query = get_record_id_by_filepath(self.batch_prefix, filepath)
        self.db_cursor.execute(sql_query)
        for i in self.db_cursor:
            return i[0]

    def add_prediction(
        self,
        record_id,
        start,
        stop,
        channel,
        predictions,
        commit=True,
        index_to_name=None,
    ):
        if index_to_name is not None:
            predictions = self.__reduce_to_known_species_array(
                predictions, index_to_name
            )

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


def drop_species_indices(collection_name, species_index_list):
    db_worker = DbWorker(collection_name)
    for species in species_index_list:
        print("Dropping index to {}".format(species))
        try:
            db_worker.drop_index(collection_name, species)
        except Exception as e:
            print(e)
            db_worker.rollback()


def create_species_indices(collection_name, species_index_list):
    db_worker = DbWorker(collection_name)
    for species in species_index_list:
        print("Adding index to {}".format(species))
        try:
            db_worker.add_index(collection_name, species)
            print("Finished adding index to species columns")
        except Exception as e:
            print(e)
            db_worker.rollback()
