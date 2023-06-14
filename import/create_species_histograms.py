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
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()  # load environment variables from .env

# Replace these variables with your own database credentials
DB_HOST = getenv("MDAS_MARIADB_HOST")
DB_USER = getenv("MDAS_MARIADB_USER")
DB_PASS = getenv("MDAS_MARIADB_PASSWORD")
DB_NAME = getenv("MDAS_MARIADB_DATABASE")
DB_PORT = int(getenv("MDAS_MARIADB_PORT"))

BIN_SIZE = 0.005


def drop_table(db_connection, tablename):
    try:
        with db_connection.cursor() as cursor:
            sql = f"DROP TABLE IF EXISTS {tablename}"
            cursor.execute(sql)
        db_connection.commit()
        debug(f"Table '{tablename}' dropped successfully.")
    except error as e:
        warn(f"Error occurred while dropping table '{tablename}': {e}")


def create_predictions_species_histogram_query(dataset_name, bin_size):
    num_bins = round(1 / bin_size)
    # Define the start of the SQL query
    sql_query = f"CREATE TABLE `{dataset_name}_species_histogram` ( \n `id` BIGINT NOT NULL AUTO_INCREMENT, \n `species` VARCHAR(255), \n"

    # Generate a column for each bin
    for i in range(num_bins):
        # Format the bin label as a float with three decimal places
        bin_label = f"`bin_{i*bin_size:.3f}` INT DEFAULT 0, \n"
        sql_query += bin_label

    # Add the primary key and index to the SQL query
    sql_query += "PRIMARY KEY (`id`), \n"
    sql_query += "INDEX `species_index` (`species` ASC)) \n ENGINE = InnoDB;"
    return sql_query


def get_all_species_names_of_prediction_tables(db_connection, dataset_name_name):
    with db_connection.cursor() as db_cursor:
        non_species_columns = ["id", "record_id", "start_time", "end_time", "channel"]
        sql_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{dataset_name_name}_predictions'"
        db_cursor.execute(sql_query)
        column_names = [column[0] for column in db_cursor.fetchall()]
        species_names = [
            column_name
            for column_name in column_names
            if column_name not in non_species_columns
        ]
        debug(f"In {dataset_name_name} found species {len(species_names)}")
    return species_names


def get_predictions_species_histogram_query(dataset_name, species_name, bin_size):
    # Define the number of bins
    num_bins = round(1 / bin_size)

    # Define the start of the SQL query
    sql_query = "SELECT "

    # Generate a CASE WHEN statement for each bin
    for i in range(num_bins):
        lower_bound = i * bin_size
        upper_bound = (i + 1) * bin_size
        bin_label = f"`bin_{i*bin_size:.3f}`"
        # print(bin_label)
        # The last bin includes the upper bound
        if i == num_bins - 1:
            case_when_stmt = f"SUM(CASE WHEN {species_name} >= {lower_bound:.3f} AND {species_name} <= {upper_bound:.3f} THEN 1 ELSE 0 END) AS {bin_label}, "
        else:
            case_when_stmt = f"SUM(CASE WHEN {species_name} >= {lower_bound:.3f} AND {species_name} < {upper_bound:.3f} THEN 1 ELSE 0 END) AS {bin_label}, "

        sql_query += case_when_stmt

    # Remove the last comma and space from the SQL query
    sql_query = sql_query[:-2]

    # Add the FROM clause to the SQL query
    sql_query += " FROM `BIRDID_AKWAMO1202A_2023_predictions` predictions;"
    # print(sql_query)
    # Print the SQL query

    return sql_query


def fill_species_histogram_table(db_connection, dataset_name, bin_size):
    num_bins = round(1 / bin_size)
    species_names = get_all_species_names_of_prediction_tables(
        db_connection, dataset_name
    )

    with db_connection.cursor() as cursor:
        for species_name in tqdm(
            species_names, desc=f"Filling species histogram for {dataset_name}"
        ):
            cursor.execute(
                get_predictions_species_histogram_query(
                    dataset_name, species_name, bin_size
                )
            )
            results = cursor.fetchall()
            bin_counts = results[0]
            # print(bin_counts)

            # Insert the histogram data into the species histogram table
            insert_query = (
                f"INSERT INTO `{dataset_name}_species_histogram` (`species`, "
            )
            for i in range(num_bins):
                insert_query += f"`bin_{i*bin_size:.3f}`, "
            insert_query = insert_query[:-2] + ") VALUES (%s, "
            for count in bin_counts:
                insert_query += "%s, "
            insert_query = insert_query[:-2] + ")"
            # print(insert_query)
            cursor.execute(insert_query, (species_name, *bin_counts))
            db_connection.commit()

    db_connection.commit()
    debug(f"Species histogram table filled for dataset {dataset_name}")


def main(partial_name=None):
    connection = mariadb.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
    )
    with connection.cursor() as db_cursor:
        db_cursor.execute("SHOW TABLES")
        tables = db_cursor.fetchall()

        dataset_names = [
            table[0][:-8] for table in tables if table[0].endswith("_records")
        ]
        tmp_string = "\n".join(dataset_names)
        debug(f"All dataset_names:\n{tmp_string}")

        if partial_name is not None:
            dataset_names = [
                dataset_name
                for dataset_name in dataset_names
                if partial_name in dataset_name
            ]
        tmp_string = "\n".join(dataset_names)
        info(f"Create Species Histogram for:\n{tmp_string}")

        for dataset_name in dataset_names:
            drop_table(connection, f"{dataset_name}_species_histogram")
            info(
                f"Start creating species histogram table for dataset {dataset_name}..."
            )
            drop_table(connection, f"{dataset_name}_species_histogram")
            db_cursor.execute(
                create_predictions_species_histogram_query(dataset_name, BIN_SIZE)
            )
            debug(f"Create Index on record_date for table {dataset_name}...")

            # Fill the species histogram table
            fill_species_histogram_table(connection, dataset_name, BIN_SIZE)

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
        help="Enable debug mode",
    )

    args = parser.parse_args()
    if args.debug:
        info("Debug mode endabled!")
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # Set the level to DEBUG
    main(
        partial_name=args.partial_name,
    )
