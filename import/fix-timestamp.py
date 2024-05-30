import mariadb
import datetime
import re
import pytz
from dotenv import load_dotenv
from os import getenv
from tqdm import tqdm

load_dotenv()  # load environment variables from .env

# Replace these variables with your own database credentials
DB_HOST = getenv("MARIADB_HOST")
DB_USER = getenv("MARIADB_USER")
DB_PASS = getenv("MARIADB_PASSWORD")
DB_NAME = getenv("MARIADB_DATABASE")
DB_PORT = int(getenv("MARIADB_PORT"))


def parse_filename(filename):
    regex = r"(\w+)_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.wav"
    match = re.match(regex, filename)
    if match:
        location = match.group(1)
        year, month, day = int(match.group(2)), int(match.group(3)), int(match.group(4))
        hour, minute, second = (
            int(match.group(5)),
            int(match.group(6)),
            int(match.group(7)),
        )
        return location, datetime.datetime(year, month, day, hour, minute, second)
    return None, None


connection = mariadb.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=DB_PORT
)


def correct_table_timestamps(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, filename, record_datetime FROM {table_name}")
        rows = cursor.fetchall()

        for row in rows:
            id, filename, current_utc_datetime = row
            location, gmt_minus_1_datetime = parse_filename(filename)
            if gmt_minus_1_datetime:
                # Convert Etc/GMT-1 to UTC
                gmt_minus_1_tz = pytz.timezone("Etc/GMT-1")
                utc_tz = pytz.UTC
                localized_datetime = gmt_minus_1_tz.localize(gmt_minus_1_datetime)
                utc_datetime = localized_datetime.astimezone(utc_tz)

                # Round both timestamps to the nearest second for comparison
                current_utc_datetime = current_utc_datetime.replace(microsecond=0)
                utc_datetime = utc_datetime.replace(microsecond=0)

                current_utc_naive = current_utc_datetime.replace(tzinfo=None)
                utc_naive = utc_datetime.replace(tzinfo=None)

                # Check if record_datetime is different and only update if needed
                if current_utc_naive != utc_naive:
                    cursor.execute(
                        f"UPDATE {table_name} SET record_datetime=%s WHERE id=%s",
                        (utc_datetime, id),
                    )
                    print(
                        f"Updated record {id} with old {current_utc_datetime} corrected timestamp {utc_datetime}"
                    )
        connection.commit()


try:
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        record_tables = [table[0] for table in tables if table[0].endswith("_records")]
        print(f"Found {len(record_tables)} tables with '_records suffix")

        for i, table_name in enumerate(record_tables, start=1):
            if "AKWAMO" in table_name:

                print(f"Processing table {i}/{len(record_tables)}: {table_name}")
                correct_table_timestamps(table_name)
finally:
    connection.close()
