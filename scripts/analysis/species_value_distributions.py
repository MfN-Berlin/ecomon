import os
import mariadb
import re
import logging
from logging import info, warn, debug
from os import getenv
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import inspect
import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()  # load environment variables from .env

# Replace these variables with your own database credentials
DB_HOST = getenv("MARIADB_HOST")
DB_USER = getenv("MARIADB_USER")
DB_PASS = getenv("MARIADB_PASSWORD")
DB_NAME = getenv("MARIADB_DATABASE")
DB_PORT = int(getenv("MARIADB_PORT"))

BIN_SIZE = 0.005
os.environ["NUMEXPR_MAX_THREADS"] = str(os.cpu_count())


def get_histogram_data_from_table(db_connection, table_name):
    # Query to retrieve histogram data for a given table
    sql_query = f"SELECT * FROM {table_name};"

    # Fetch the data into a pandas DataFrame
    df = pd.read_sql(sql_query, con=db_connection, index_col="species")
    df.drop(columns=["id"], inplace=True, errors="ignore")

    debug(f"Retrieved histogram data for {len(df)} species from {table_name}.")

    return df


def calculate_integral(series):
    # Calculate the integral (cumulative sum) over the bins
    integral = series.cumsum()
    return integral


def main(prefix):
    connection = mariadb.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
    )

    # Get the list of table names that match the specified pattern
    with connection.cursor() as db_cursor:
        db_cursor.execute("SHOW TABLES")
        tables = db_cursor.fetchall()
        table_names = [
            table[0]
            for table in tables
            if re.match(rf"^{prefix}.*_species_histogram$", table[0])
        ]

    if not table_names:
        warn(f"No tables matching the specified pattern found with prefix {prefix}.")
        return

    info(
        f"Found {len(table_names)} tables matching the specified pattern with prefix {prefix}."
    )

    total_counts = None
    for table_name in table_names:
        df = get_histogram_data_from_table(connection, table_name)
        # log df dimensions
        has_nan = df.isna().any().any()

        if has_nan:
            warn(f"The {table_name} includes will not be added NaN values.")
        else:
            if total_counts is None:
                total_counts = df
            else:
                total_counts += df

    # Calculate overall distribution

    overall_count = total_counts.sum().sum()
    overall_distribution = total_counts.sum() / overall_count
    debug(f"Overall distribution: \n{overall_distribution}")

    # Calculate species distribution
    zero_sum_species = total_counts[total_counts.sum(axis=1) == 0].index
    info(f"Found {len(zero_sum_species)} species with zero sum.")
    info(f"Species with zero sum: {zero_sum_species}")
    total_counts.drop(zero_sum_species, inplace=True)
    info(total_counts)
    species_distribution = total_counts.div(total_counts.sum(axis=1), axis=0)

    debug(f"Species distribution: \n{species_distribution}")

    # Calculate integral over the bins for each species distribution

    species_integral = species_distribution.apply(calculate_integral, axis=1)
    debug(f"Integral over the bins for each species distribution: \n{species_integral}")

    # Calculate integral over the bins for the overall distribution
    overall_integral = overall_distribution.cumsum()
    debug(f"Integral over the bins for the overall distribution: \n{overall_integral}")

    connection.close()

    # Create a new DataFrame for the overall integral
    overall_integral_df = pd.DataFrame(
        overall_integral.values.reshape(1, -1),
        index=["overall"],
        columns=overall_integral.index,
    )
    # Concatenate the overall integral DataFrame with the species integral DataFrame
    species_integral = pd.concat([overall_integral_df, species_integral])

    # Save the species integral DataFrame as CSV
    script_filename = os.path.splitext(os.path.basename(inspect.stack()[0][1]))[0]
    output_folder = f"{script_filename}_results"
    os.makedirs(output_folder, exist_ok=True)
    output_csv = os.path.join(output_folder, f"{prefix}_species_integral.csv")
    species_integral.to_csv(output_csv, index_label="species")

    # Plot the integral for each species
    plt.figure()
    for species in species_integral.index:
        plt.plot(species_integral.loc[species], label=species)

    plt.xlabel("Threshold")
    plt.ylabel("Integral")
    plt.title("Integral over the Bins for Species Distributions")
    plt.legend()
    output_plot = os.path.join(output_folder, f"{prefix}_species_integral_plot.png")
    plt.savefig(output_plot)
    plt.show()


if __name__ == "__main__":
    logging.info("Starting species_value_distributions.py...")
    prefixes = ["BIRDNET"]
    for prefix in prefixes:
        info(f"Running for {prefix}...")
        main(prefix)
