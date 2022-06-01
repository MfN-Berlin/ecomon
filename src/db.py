from telnetlib import NOP
import mariadb
import sys
import os


import sql.initial as queries


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


def init_db(batch_prefix):
    db_connection = connect_to_db()
    db_cursor = db_connection.cursor()
    records_exists = False
    predictions_exists = False
    records_count = 0
    predictions_count = 0
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
        NOP

    if records_exists or predictions_exists:
        line = ""
        while line != "y":
            line = input("Tables already exists do you want to resume analysis? (y/n):")
            if line == "n":
                sys.exit(1)

    if not records_exists:
        print("Create {}_records table".format(batch_prefix))
        db_cursor.execute(queries.create_record_table(batch_prefix))
        db_connection.commit()
    if not predictions_exists:
        print("Create {}_predictions table".format(batch_prefix))
        db_cursor.execute(queries.create_predictions_table(batch_prefix))
        db_connection.commit()
    db_connection.close()

