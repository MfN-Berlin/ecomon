import argparse
from datetime import datetime
import os
import json
import mariadb
import pandas as pd
from tqdm import tqdm
from os import getenv, path
from dotenv import load_dotenv
from util.files import check_audio_file
from json import JSONEncoder
import decimal
from pytz import timezone, utc


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(CustomJSONEncoder, self).default(obj)


def create_json_file(report_data, report_path):
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2, cls=CustomJSONEncoder)


def createYearMonthDayList(year):
    yearMonthDayList = []
    for month in range(1, 13):
        for day in range(1, 32):
            try:
                yearMonthDayList.append(datetime(year, month, day).strftime("%Y/%m/%d"))
            except ValueError:
                pass
    return yearMonthDayList


def report(
    cursor, table_name, predictions_table, queries, report_path, output_format="text"
):
    report_data = {}
    cursor.execute(queries[0][1])
    result = cursor.fetchone()

    if result is None:
        if output_format == "text":
            with open(report_path, "w") as f:
                f.write(f"No files in collection\n")
        elif output_format == "json":
            create_json_file({"message": "No files in collection"}, report_path)
        print(f"No files in collection {table_name}")
        return

    first_datetime = result[0]
    cursor.execute(queries[1][1])
    last_datetime = cursor.fetchone()[0]

    # Convert the datetime objects to the "Etc/GMT-1" timezone
    desired_tz = timezone("Etc/GMT-1")
    first_datetime_tz = first_datetime.replace(tzinfo=utc).astimezone(desired_tz)
    last_datetime_tz = last_datetime.replace(tzinfo=utc).astimezone(desired_tz)

    # Convert first_datetime to UTC datetime string
    first_datetime_utc = first_datetime_tz.replace(tzinfo=timezone("UTC")).astimezone(
        utc
    )
    report_data["first_record_datetime"] = first_datetime_utc.isoformat()

    # Convert last_datetime to UTC datetime string
    last_datetime_utc = last_datetime_tz.replace(tzinfo=timezone("UTC")).astimezone(utc)
    report_data["last_record_datetime"] = last_datetime_utc.isoformat()

    for query_name, query_template in queries[2:]:
        query = query_template.format(
            records_table=table_name, predictions_table=predictions_table
        )
        cursor.execute(query)
        result = cursor.fetchall()

        if output_format == "text":
            formatted_key = query_name.replace("_", " ").title()
        else:
            formatted_key = query_name

        if query_name.endswith("_histogram_query"):

            if query_name == "record_duration_histogram_query":
                report_data[formatted_key] = [
                    {"duration": row[0], "record_count": row[1]} for row in result
                ]
            elif query_name == "record_prediction_count_histogram_query":
                report_data[formatted_key] = [
                    {"prediction_count": row[0], "record_count": row[1]}
                    for row in result
                ]
            else:
                report_data[formatted_key] = [{str(row[0]): row[1]} for row in result]
        # elif query_name.endswith("daily_summary_query"):
        #     report_data[formatted_key] = [
        #         {
        #             "date": f"{row[0]}/{row[1]}/{row[2]}",
        #             "count": row[3],
        #             "duration": row[4],
        #         }
        #         for row in result
        #     ]
        elif query_name.endswith("daily_summary_query"):
            daily_summary = {}
            for row in result:
                date_str = f"{row[0]}/{row[1]}/{row[2]}"
                daily_summary[date_str] = {
                    "count": row[3],
                    "duration": row[4],
                    "prediction_count": row[5],
                }

            year = last_datetime.year

            for date_str in createYearMonthDayList(year):

                if date_str not in daily_summary:
                    daily_summary[date_str] = {
                        "count": 0,
                        "duration": 0,
                        "prediction_count": 0,
                    }

            report_data[formatted_key] = [
                {
                    "date": date_str,
                    "count": daily_summary[date_str]["count"],
                    "duration": daily_summary[date_str]["duration"],
                    "prediction_count": daily_summary[date_str]["prediction_count"],
                }
                for date_str in sorted(daily_summary.keys())
            ]
        # elif query_name.endswith("monthly_summary_query"):
        #     report_data[formatted_key] = [
        #         {"date": f"{row[0]}/{row[1]}", "count": row[2], "duration": row[3],}
        #         for row in result
        #     ]
        elif query_name.endswith("monthly_summary_query"):
            result_dict = {
                (row[0], row[1]): {"count": row[2], "duration": row[3]}
                for row in result
            }
            report_data[formatted_key] = []

            year = last_datetime.year

            for month in range(1, 12):
                key = (year, month)
                if key in result_dict:
                    report_data[formatted_key].append(
                        {"date": f"{year}/{month:02d}", **result_dict[key]}
                    )
                else:
                    report_data[formatted_key].append(
                        {"date": f"{year}/{month:02d}", "count": 0, "duration": 0}
                    )

        else:
            report_data[formatted_key] = result[0][0]

    if output_format == "text":
        with open(report_path, "w") as f:
            for key, value in report_data.items():
                f.write(f"{key}: {value}\n")
                f.write("\n")
    elif output_format == "json":
        create_json_file(report_data, report_path)


# create a connection to the MySQL database
def create_report(prefix=None, output_format="json"):
    load_dotenv()
    root_dir = getenv("MDAS_DATA_DIRECTORY")

    cnx = mariadb.connect(
        user=getenv("MDAS_MARIADB_USER"),
        password=getenv("MDAS_MARIADB_PASSWORD"),
        database=getenv("MDAS_MARIADB_DATABASE"),
        host=getenv("MDAS_MARIADB_HOST"),
        port=int(getenv("MDAS_MARIADB_PORT")),
    )

    cursor = cnx.cursor()

    REPORTS_DIR = "./reports"
    if prefix is not None:
        prefixes = [prefix]
    else:
        cursor.execute("SHOW TABLES LIKE '%\\_records'")
        tables = cursor.fetchall()
        prefixes = [table[0][: -len("_records")] for table in tables]

    for prefix in prefixes:
        table_name = f"{prefix}_records"
        predictions_table = f"{prefix}_predictions"

        report_extension = "json" if output_format == "json" else "txt"
        report_name = f"{prefix}_report.{report_extension}"
        report_path = os.path.join(REPORTS_DIR, report_name)

        queries = [
            (
                "first_record_query",
                f"SELECT record_datetime FROM {table_name} ORDER BY record_datetime LIMIT 1;",
            ),
            (
                "last_record_query",
                f"SELECT record_datetime FROM {table_name} ORDER BY record_datetime DESC LIMIT 1;",
            ),
            ("records_count", f"SELECT COUNT(*) FROM {table_name};"),
            (
                "corrupted_record_count",
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
                f"""
        SELECT YEAR(CONVERT_TZ({table_name}.record_datetime, '+00:00', '-01:00')) AS year, MONTH(CONVERT_TZ({table_name}.record_datetime, '+00:00', '-01:00')) AS month, COUNT(DISTINCT {table_name}.id) AS record_count, SUM({table_name}.duration) AS total_duration, COUNT({predictions_table}.id) AS prediction_count
        FROM {table_name}
        LEFT JOIN {predictions_table} ON {table_name}.id = {predictions_table}.record_id
        GROUP BY YEAR(CONVERT_TZ({table_name}.record_datetime, '+00:00', '+01:00')), MONTH(CONVERT_TZ({table_name}.record_datetime, '+00:00', '-01:00'));
        """,
            ),
            (
                "daily_summary_query",
                f"""
        SELECT YEAR(CONVERT_TZ({table_name}.record_datetime, '+00:00', '-01:00')) AS year, LPAD(MONTH(CONVERT_TZ({table_name}.record_datetime, '+00:00', '-01:00')), 2, '0') AS month, LPAD(DAY(CONVERT_TZ({table_name}.record_datetime, '+00:00', '-01:00')), 2, '0') AS day, COUNT(DISTINCT {table_name}.id) AS record_count, SUM({table_name}.duration) AS total_duration, COUNT({predictions_table}.id) AS prediction_count
        FROM {table_name}
        LEFT JOIN {predictions_table} ON {table_name}.id = {predictions_table}.record_id
        GROUP BY YEAR(CONVERT_TZ({table_name}.record_datetime, '+00:00', '+01:00')), MONTH(CONVERT_TZ({table_name}.record_datetime, '+00:00', '-01:00')), DAY(CONVERT_TZ({table_name}.record_datetime, '+00:00', '-01:00'));
        """,
            ),
        ]

        print(f"Creating {output_format} report for {table_name} at {report_path}...")

        report(
            cursor,
            table_name,
            predictions_table,
            queries,
            report_path,
            output_format=output_format,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate report for a collection")
    parser.add_argument(
        "collection_prefix",
        nargs="?",
        help="Collection/prefix name (optional)",
        default=None,
    )
    parser.add_argument(
        "output_format",
        nargs="?",
        default="json",
        choices=["text", "json"],
        help="Output format: 'text' for text format or 'json' for JSON format (default: 'text')",
    )

    args = parser.parse_args()
    create_report(prefix=args.collection_prefix, output_format=args.output_format)

