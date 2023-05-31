import argparse
import mariadb
import datetime
import re
import pytz
from dotenv import load_dotenv
from os import getenv
from tqdm import tqdm
import logging
from logging import debug, info, warn
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()  # load environment variables from .env

# Replace these variables with your own database credentials
DB_HOST = getenv("MDAS_MARIADB_HOST")
DB_USER = getenv("MDAS_MARIADB_USER")
DB_PASS = getenv("MDAS_MARIADB_PASSWORD")
DB_NAME = getenv("MDAS_MARIADB_DATABASE")
DB_PORT = int(getenv("MDAS_MARIADB_PORT"))



def drop_table(db_connection, tablename):
    try:
        with db_connection.cursor() as cursor:
            sql = f"DROP TABLE IF EXISTS {tablename}"
            cursor.execute(sql)
        db_connection.commit()
        debug(f"Table '{tablename}' dropped successfully.")
    except error as e:
        warn(f"Error occurred while dropping table '{tablename}': {e}")

def create_predictions_max_table(dataset_name, species): 
    rows = " ".join([f"  `{s}` FLOAT NOT NULL,\n" for s in species])
    return """
CREATE TABLE `{p}_predictions_max` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `record_id` INT NOT NULL,
    {r}
    PRIMARY KEY (`id`),
    FOREIGN KEY (`record_id`) REFERENCES `{p}_records` (`id`) ON DELETE CASCADE,
    UNIQUE INDEX `id_UNIQUE` (`id` ASC),
    UNIQUE INDEX `record_index` (`record_id` ASC)

);
    """.format(
        p=dataset_name, r=rows
    )



def create_predictions_max_table_query(dataset_name, species): 
    rows = ",".join([f"MAX(p.{s}) AS {s}\n" for s in species])
    query_string = """
CREATE TABLE `{ds}_predictions_max` AS 
SELECT p.record_id,
       r.record_datetime,
       {rows}
FROM bai.{ds}_predictions as p
JOIN {ds}_records AS r ON p.record_id = r.id
GROUP BY p.record_id
ORDER BY r.record_datetime ASC
    """.format(
        ds=dataset_name, rows=rows
    )
    # debug(query_string)
    return query_string


def add_index_to_prediction_max_qery(dataset_name):
    index_query = """
CREATE INDEX idx_record_datetime
ON `{ds}_predictions_max` (record_datetime ASC);
""".format(ds=dataset_name)
    # debug(index_query)
    return index_query
    

def get_all_species_names_of_prediction_tables(db_connection, dataset_name_name):
    with db_connection.cursor() as db_cursor:
        non_species_columns= [ 'id','record_id','start_time','end_time','channel']
        sql_query= f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{dataset_name_name}_predictions'"
        db_cursor.execute(sql_query)
        column_names = [column[0] for column in db_cursor.fetchall()]
        species_names = [column_name for column_name in column_names if column_name not in non_species_columns]
        debug(f'In {dataset_name_name} found species {len(species_names)}')
    return species_names

def main(partial_name=None):
    connection = mariadb.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
    )
    with connection.cursor() as db_cursor:
        db_cursor.execute("SHOW TABLES")
        tables = db_cursor.fetchall()

        dataset_names = [table[0][:-8] for table in tables if table[0].endswith("_records")]
        tmp_string = '\n'.join(dataset_names)
        debug(f"All dataset_names:\n{tmp_string}")

        if partial_name is not None:
            dataset_names = [dataset_name for dataset_name in dataset_names if partial_name in dataset_name]
        tmp_string = '\n'.join(dataset_names)
        info(f"Create Species Histogram for: \n{tmp_string}")

        for dataset_name in dataset_names:
            species_list = get_all_species_names_of_prediction_tables(connection,dataset_name)
            drop_table(connection,f'{dataset_name}_predictions_max')
            info(f'start creating max for table {dataset_name}...')
            db_cursor.execute(create_predictions_max_table_query(dataset_name,species_list))
            debug(f'create Index on record_date for table {dataset_name}...')
            db_cursor.execute(add_index_to_prediction_max_qery(dataset_name))
            connection.commit()


    connection.close()             


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
        help="Enable debug mode"
    )
   

    args = parser.parse_args()
    if(args.debug):
        info("Debug mode endabled!")
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Set the level to DEBUG
    main(
        partial_name=args.partial_name,
    )

