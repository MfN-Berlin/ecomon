import argparse
import psycopg2
from psycopg2 import sql
import datetime
import re
import pytz
from dotenv import load_dotenv
from os import getenv
from tqdm import tqdm
import logging
from logging import debug, info, warn
from multiprocessing import Pool

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()  # load environment variables from .env

# Replace these variables with your own database credentials
DB_HOST = getenv("POSTGRES_HOST")
DB_USER = getenv("POSTGRES_USER")
DB_PASS = getenv("POSTGRES_PASSWORD")
DB_NAME = getenv("POSTGRES_DATABASE")
DB_PORT = int(getenv("POSTGRES_PORT"))
DATABASE_NAME = getenv("POSTGRES_DATABASE")


def drop_table(db_connection, tablename):
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(tablename)))
        db_connection.commit()
        debug(f"Table '{tablename}' dropped successfully.")
    except psycopg2.Error as e:
        warn(f"Error occurred while dropping table '{tablename}': {e}")


def create_predictions_max_table(dataset_name, species):
    rows = " ".join([f"  {s} FLOAT NOT NULL,\n" for s in species])
    return f"""
CREATE TABLE {dataset_name}_predictions_max (
    id BIGSERIAL PRIMARY KEY,
    record_id INT NOT NULL,
    {rows}
    FOREIGN KEY (record_id) REFERENCES {dataset_name}_records (id) ON DELETE CASCADE,
    UNIQUE (record_id)
);
"""


def create_predictions_max_table_query(dataset_name, species):
    rows = ", ".join([f"MAX(p.{s}) AS {s}" for s in species])
    return f"""
CREATE TABLE {dataset_name}_predictions_max AS
SELECT p.record_id,
       r.record_datetime,
       {rows}
FROM {dataset_name}_predictions AS p
JOIN {dataset_name}_records AS r ON p.record_id = r.id
GROUP BY p.record_id, r.record_datetime
ORDER BY r.record_datetime ASC;
"""


def add_index_to_prediction_max_query(dataset_name):
    return f"""
CREATE INDEX IF NOT EXISTS idx_record_datetime
ON {dataset_name}_predictions_max (record_datetime ASC);
"""


def get_all_species_names_of_prediction_tables(db_connection, dataset_name_name):
    with db_connection.cursor() as db_cursor:
        non_species_columns = ["id", "record_id", "start_time", "end_time", "channel"]
        sql_query = sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = %s")
        db_cursor.execute(sql_query, (f"{dataset_name_name}_predictions",))
        column_names = [column[0] for column in db_cursor.fetchall()]
        species_names = [
            column_name
            for column_name in column_names
            if column_name not in non_species_columns
        ]
        debug(f"In {dataset_name_name} found species {len(species_names)}")
    return species_names


def worker(datasets):
    connection = psycopg2.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
    )
    with connection.cursor() as db_cursor:
        for dataset_name in datasets:
            species_list = get_all_species_names_of_prediction_tables(
                connection, dataset_name
            )
            drop_table(connection, f"{dataset_name}_predictions_max")
            info(f"start creating max for table {dataset_name}...")
            db_cursor.execute(create_predictions_max_table_query(dataset_name, species_list))
            debug(f"create Index on record_date for table {dataset_name}...")
            db_cursor.execute(add_index_to_prediction_max_query(dataset_name))
            connection.commit()
    connection.close()


def main(partial_name=None, cores=1):
    with psycopg2.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
    ) as connection:
        with connection.cursor() as db_cursor:
            db_cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s", ('%_records',))
            tables = db_cursor.fetchall()
            info(f"Found {len(tables)} tables")
            dataset_names = [
                table[0][:-8] for table in tables if table[0].endswith("_records")
            ]
            info(f"Found {len(dataset_names)} dataset names")
            
            if partial_name is not None:
                dataset_names = [
                    dataset_name
                    for dataset_name in dataset_names
                    if partial_name in dataset_name
                ]
            info(f"Found {dataset_names} dataset names")
            chunk_size = len(dataset_names) // cores
            datasets_split = [
                dataset_names[i : i + chunk_size]
                for i in range(0, len(dataset_names), chunk_size)
            ]

    with Pool(cores) as p:
        p.map(worker, datasets_split)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate report for a collection")
    parser.add_argument(
        "partial_name",
        nargs="?",
        help="Collection/prefix name or part of the name(optional)",
        default=None,
    )
    parser.add_argument(
        "--debug",
        action="store_true",  # Use action="store_true" for boolean flags
        help="Enable debug mode",
    )
    parser.add_argument(
        "--cores",
        type=int,
        default=1,
        help="Number of CPU cores to use for the processing. Default is 1.",
    )

    args = parser.parse_args()
    if args.debug:
        info("Debug mode enabled!")
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Set the level to DEBUG

    main(partial_name=args.partial_name, cores=args.cores)
