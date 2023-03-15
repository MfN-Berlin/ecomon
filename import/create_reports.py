import os

import mariadb
from tqdm import tqdm
from os import getenv, path
from dotenv import load_dotenv
from util.files import check_audio_file

# create a connection to the MySQL database
load_dotenv()  # load environment variables from .env

root_dir = getenv("MDAS_DATA_DIRECTORY")

cnx = mariadb.connect(
    user=getenv("MDAS_MARIADB_USER"),
    password=getenv("MDAS_MARIADB_PASSWORD"),
    database=getenv("MDAS_MARIADB_DATABASE"),
    host=getenv("MDAS_MARIADB_HOST"),
    port=int(getenv("MDAS_MARIADB_PORT")),
)

# create a cursor object
cursor = cnx.cursor()


# define the directory where the reports will be saved
REPORTS_DIR = "./reports"
cursor.execute("SHOW TABLES LIKE '%\_records'")
tables = cursor.fetchall()
# iterate over tables ending with "_records"
for table in tables:
    table_name = table[0]
    if not table_name.endswith("_records"):
        continue

    # determine the corresponding predictions table
    prefix = table_name[: -len("_records")]
    predictions_table = f"{prefix}_predictions"

    # define the SQL statements to execute
    queries = [
        (
            "first_record_query",
            f"SELECT record_datetime FROM {table_name} ORDER BY id LIMIT 1;",
        ),
        (
            "last_record_query",
            f"SELECT record_datetime FROM {table_name} ORDER BY id DESC LIMIT 1;",
        ),
        ("records_count", f"SELECT COUNT(*) FROM {table_name};"),
        (
            "corrupted_record_count_query",
            f"SELECT COUNT(*) FROM {table_name} WHERE corrupted > 0;",
        ),
        ("summed_records_duration", f"SELECT SUM(duration) FROM {table_name};",),
        ("predictions_count", f"SELECT COUNT(*) FROM {predictions_table};"),
        (
            "record_duration_histogram_query",
            f"SELECT FLOOR(duration) AS duration_range, COUNT(*) AS count FROM {table_name} GROUP BY duration_range ORDER BY duration_range",
        ),
        (
            "record_prediction_count_histogram_query",
            """
            SELECT prediction_count, COUNT(*) AS frequency
            FROM (
                SELECT {records_table}.id, COUNT({predictions_table}.id) AS prediction_count
                FROM {records_table} LEFT JOIN {predictions_table} ON {records_table}.id = {predictions_table}.record_id
                GROUP BY {records_table}.id
            ) AS counts
            GROUP BY prediction_count;
        """,
        ),
        (
            "monthly_summary_query",
            """
            SELECT YEAR({records_table}.record_datetime) AS year, MONTH({records_table}.record_datetime) AS month, COUNT(DISTINCT {records_table}.id) AS record_count, SUM({records_table}.duration) AS total_duration, COUNT({predictions_table}.id) AS prediction_count
            FROM {records_table}
            LEFT JOIN {predictions_table} ON {records_table}.id = {predictions_table}.record_id
            GROUP BY YEAR({records_table}.record_datetime), MONTH({records_table}.record_datetime);
        """,
        ),
        (
            "daily_summary_query",
            """
            SELECT YEAR({records_table}.record_datetime) AS year, MONTH({records_table}.record_datetime), DAY({records_table}.record_datetime) AS day, COUNT(DISTINCT {records_table}.id) AS record_count, SUM({records_table}.duration) AS total_duration, COUNT({predictions_table}.id) AS prediction_count
            FROM {records_table}
            LEFT JOIN {predictions_table} ON {records_table}.id = {predictions_table}.record_id
            GROUP BY YEAR({records_table}.record_datetime), MONTH({records_table}.record_datetime), DAY({records_table}.record_datetime);
        """,
        ),
    ]

    report_name = f"{prefix}_report.txt"
    report_path = os.path.join(REPORTS_DIR, report_name)
    print(f"Creating report for {table_name} at {report_path}...")
    with open(report_path, "w") as f:
        # save the datetime for the first and last record
        cursor.execute(queries[0][1])
        result = cursor.fetchone()
        # check if result is NoneTyoe
        if result is None:
            f.write(f"No files in collection\n")
            print(f"No files in collection {table_name}")
            continue

        first_datetime = result[0]
        cursor.execute(queries[1][1])
        last_datetime = cursor.fetchone()[0]
        f.write(f"First Record Datetime: {first_datetime}\n")
        f.write(f"Last Record Datetime: {last_datetime}\n")
        # save the other stats
        for query_name, query_template in queries[2:]:
            query = query_template.format(
                records_table=table_name, predictions_table=predictions_table
            )
            cursor.execute(query)
            result = cursor.fetchall()
            if query_name == "record_prediction_count_histogram_query":
                f.write("\n")
                f.write("**Record-Prediction Count Histogram**\n")
                f.write(f"Predictions count,\tRecords\n")
                for row in result:
                    count = row[0]
                    frequency = row[1]
                    f.write(f"{count},\t {frequency}\n")
            elif query_name == "monthly_summary_query":
                f.write("\n")
                f.write("**Monthly Record Histogram**\n")
                f.write(f"Date,\tCount,\tRecord Duration\n")
                for row in result:
                    year = row[0]
                    month = row[1]
                    count = row[2]
                    duration = row[3]
                    f.write(f"{year}/{month},\t{count},\t{duration}\n")
            elif query_name == "record_duration_histogram_query":
                f.write("\n")
                f.write("**Record Duration Histogram**\n")
                f.write(f"Duration,\tRecords\n")
                for row in result:
                    duration = row[0]
                    count = row[1]
                    f.write(f"{duration},\t{count}\n")
            elif query_name == "daily_summary_query":
                f.write("\n")
                f.write("**Daily Record Histogram**\n")
                f.write(f"Date,\tCount,\tRecord Duration\n")
                for row in result:
                    year = row[0]
                    month = row[1]
                    day = row[2]
                    count = row[3]
                    duration = row[4]
                    f.write(f"{year}/{month}/{day},\t{count},\t{duration}\n")
            else:
                f.write(f'{query_name.replace("_", " ").title()}: {result[0][0]}\n')
        f.write("\n")
