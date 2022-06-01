from time import sleep
from tqdm import tqdm
import mariadb
import sys
import os


def connect_to_db():
    try:
        conn = mariadb.connect(
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
    return conn.cursor()


def store_loop_factory(
    processed_files_filepath,
    all_analyzed_event,
    results_queue,
    processed_count,
    files_count,
):
    db_cursor = connect_to_db()

    def loop():

        with tqdm(
            total=files_count,
            initial=processed_count,
            desc="Analyzed",
            unit="files",
            smoothing=0.1,
        ) as progress:

            with open(processed_files_filepath, "a") as processed_f:
                while not results_queue.empty() or not all_analyzed_event.is_set():
                    if results_queue.empty():
                        sleep(1)
                        continue
                    filepath = results_queue.get()
                    # print("store {}".format(filepath[1]))
                    # write filepath to processed to file
                    processed_f.write(filepath[0] + "\n")
                    processed_f.flush()
                    progress.update(1)
                    sleep(0.1)

    return loop
