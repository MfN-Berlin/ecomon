import os
import pandas as pd
from airflow.decorators import dag, task
from datetime import datetime
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook

@dag(
    dag_id='create_report',
    schedule='0 * * * *',  # every hour at minute 0
    start_date=datetime(2025, 12, 1),
    catchup=False,
)
def create_report():

    @task
    def get_sites_from_db():
        """Fetch site id and prefix from the database"""
        # Use Airflow's Postgres hook
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        query = "SELECT id, prefix FROM sites ORDER BY id"

        # Execute query and fetch results
        records = postgres_hook.get_records(query)
        sites = [{"site_id": row[0], "prefix": row[1]} for row in records]

        logging.info(f"Found {len(sites)} sites in database")
        return sites

    @task
    def get_record_counts_from_db(sites):
        """Fetch record counts for each site from the database"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        record_counts = {}

        for site in sites:
            site_id = site["site_id"]
            query = f"SELECT COUNT(id) FROM records WHERE site_id = {site_id}"

            # Execute query and fetch result
            result = postgres_hook.get_first(query)
            record_counts[site_id] = result[0] if result else 0

        logging.info(f"Fetched record counts for {len(record_counts)} sites")
        return record_counts

    @task
    def get_birdid_medium_processed_counts(sites):
        """Fetch BirdId-medium processed record counts for each site from the database"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        birdid_medium_counts = {}

        for site in sites:
            site_id = site["site_id"]
            query = f"""
            WITH tmp_record_ids AS (
                SELECT id
                FROM records
                WHERE site_id = {site_id}
            )
            SELECT count(distinct(mil.record_id))
            FROM model_inference_logs AS mil
            WHERE mil.record_id = ANY (ARRAY(SELECT id FROM tmp_record_ids))
            AND mil.model_id=3
            """

            # Execute query and fetch result
            result = postgres_hook.get_first(query)
            birdid_medium_counts[site_id] = result[0] if result else 0

        logging.info(f"Fetched BirdId Medium processed counts for {len(birdid_medium_counts)} sites")
        return birdid_medium_counts

    @task
    def scan_directories():
        """Get list of directories to process (memory efficient)"""
        import os

        BASE_DIR = '/data'

        logging.info(f"Starting directory scan of {BASE_DIR}")

        if not os.path.isdir(BASE_DIR):
            raise ValueError(f"Not a valid directory {BASE_DIR}")

        directories = []

        # Use scandir for better performance
        try:
            logging.info("Scanning first level (prefix directories)...")
            # First level: prefix directories
            with os.scandir(BASE_DIR) as prefix_entries:
                prefix_count = 0
                for prefix_entry in prefix_entries:
                    if prefix_entry.is_dir():
                        prefix_name = prefix_entry.name
                        prefix_count += 1
                        logging.info(f"Processing prefix directory: {prefix_name}")

                        # Second level: date directories
                        try:
                            with os.scandir(prefix_entry.path) as date_entries:
                                date_dir_count = 0
                                for date_entry in date_entries:
                                    if date_entry.is_dir():
                                        # Build relative path: PREFIX/PREFIX_DATE
                                        rel_path = f"{prefix_name}/{date_entry.name}"
                                        directories.append(rel_path)
                                        date_dir_count += 1

                                logging.info(f"  Found {date_dir_count} date directories in {prefix_name}")

                        except PermissionError as e:
                            logging.warning(f"Permission denied accessing {prefix_entry.path}: {e}")
                            continue

                logging.info(f"Scanned {prefix_count} prefix directories")

        except PermissionError as e:
            logging.error(f"Permission denied accessing {BASE_DIR}: {e}")
            raise

        logging.info(f"Directory scan complete. Found {len(directories)} total directories to process")
        return directories

    @task
    def get_last_report_dates_by_directory():
        """Get the last report date for each directory"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        query = """
        SELECT prefix, MAX(report_date) as last_report_date
        FROM workflow_reports
        GROUP BY prefix
        """

        records = postgres_hook.get_records(query)

        # Create a dictionary mapping prefix to last report date
        last_dates = {}
        for row in records:
            if row and row[0] and row[1]:
                last_dates[row[0]] = row[1]

        logging.info(f"Found last report dates for {len(last_dates)} prefixes")
        return last_dates

    @task
    def list_wavs(directories, sites, last_report_dates):
        """Count WAV files and calculate sizes only for directories modified since their last report"""

        # Create a set of valid prefixes from sites
        valid_prefixes = {site["prefix"] for site in sites}
        logging.info(f"Valid site prefixes: {valid_prefixes}")

        result = []
        skipped_count = 0
        processed_count = 0
        no_previous_report_count = 0

        for directory in directories:
            # Extract prefix from directory (e.g., "TEST/TEST_20230506" -> "TEST")
            prefix = directory.split("/")[0]

            # Skip directories that don't match any site prefix
            if prefix not in valid_prefixes:
                logging.debug(f"Skipping directory {directory} (prefix '{prefix}' not in valid sites)")
                continue

            full_path = os.path.join('/data', directory)

            try:
                # Check directory modification time (works with s3fs)
                dir_stat = os.stat(full_path)
                dir_mtime = dir_stat.st_mtime
                dir_mtime_dt = datetime.fromtimestamp(dir_mtime)

                # Get last report date for this prefix
                last_report_date = last_report_dates.get(prefix)

                if last_report_date:
                    # Convert to datetime if it's a string
                    if isinstance(last_report_date, str):
                        last_report_timestamp = datetime.fromisoformat(last_report_date).timestamp()
                    else:
                        last_report_timestamp = last_report_date.timestamp()

                    # Skip if directory hasn't been modified since last report for this prefix
                    if dir_mtime < last_report_timestamp:
                        logging.debug(f"Skipping {directory} (last modified: {dir_mtime_dt}, last report: {last_report_date})")
                        skipped_count += 1
                        continue

                    logging.info(f"Processing {directory} (modified: {dir_mtime_dt}, last report: {last_report_date})")
                else:
                    logging.info(f"Processing {directory} (no previous report for prefix '{prefix}')")
                    no_previous_report_count += 1

                # Count WAV files and calculate total size
                wav_count = 0
                total_size = 0

                for filename in os.listdir(full_path):
                    if filename.lower().endswith('.wav'):
                        wav_count += 1
                        file_path = os.path.join(full_path, filename)
                        try:
                            total_size += os.path.getsize(file_path)
                        except OSError as e:
                            logging.warning(f"Could not get size of {file_path}: {e}")

                result.append({
                    "directory": directory,
                    "wav_count": wav_count,
                    "wav_size_bytes": total_size
                })
                processed_count += 1

            except OSError as e:
                logging.error(f"Error processing directory {full_path}: {e}")
                continue

        logging.info(f"Processed {processed_count} directories ({no_previous_report_count} new prefixes), "
                    f"skipped {skipped_count} unchanged directories (from {len(directories)} total)")
        return result

    @task
    def aggregate_wav_data_by_prefix(rows, sites, last_report_dates):
        """Aggregate WAV file counts and sizes by prefix, using last report data for unchanged prefixes"""

        # Create a lookup dictionary from prefix to site_id
        prefix_to_site = {site["prefix"]: site["site_id"] for site in sites}

        # Get last report data for all prefixes
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        query = """
        SELECT DISTINCT ON (prefix)
            prefix, wav_count, wav_size_bytes
        FROM workflow_reports
        ORDER BY prefix, report_date DESC
        """

        last_report_records = postgres_hook.get_records(query)

        # Dictionary to store aggregated data by prefix
        prefix_data = {}

        # Initialize with last known data for all sites
        for record in last_report_records:
            if record and record[0]:
                prefix = record[0]
                if prefix in prefix_to_site:  # Only include valid prefixes
                    prefix_data[prefix] = {
                        "prefix": prefix,
                        "site_id": prefix_to_site.get(prefix),
                        "wav_count": record[1] or 0,
                        "wav_size_bytes": record[2] or 0
                    }

        # Update with new scanned data (overwrites old data for changed prefixes)
        for row in rows:
            # Extract prefix from directory (e.g., "TEST/TEST_20230506" -> "TEST")
            prefix = row["directory"].split("/")[0]

            # Initialize prefix entry if it doesn't exist
            if prefix not in prefix_data:
                prefix_data[prefix] = {
                    "prefix": prefix,
                    "site_id": prefix_to_site.get(prefix),
                    "wav_count": 0,
                    "wav_size_bytes": 0
                }

            # Aggregate the counts and sizes
            prefix_data[prefix]["wav_count"] += row["wav_count"]
            prefix_data[prefix]["wav_size_bytes"] += row["wav_size_bytes"]

        # Add any sites that have never been reported
        for site in sites:
            prefix = site["prefix"]
            if prefix not in prefix_data:
                prefix_data[prefix] = {
                    "prefix": prefix,
                    "site_id": site["site_id"],
                    "wav_count": 0,
                    "wav_size_bytes": 0
                }

        logging.info(f"Aggregated data for {len(prefix_data)} prefixes ({len(rows)} newly scanned)")
        return list(prefix_data.values())

    @task
    def get_running_inference_jobs():
        """Fetch running model inference jobs from the database"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        query = """
        SELECT metadata
        FROM jobs
        WHERE status='running'
        AND topic='model_inference_site'
        """

        # Execute query and fetch results
        records = postgres_hook.get_records(query)

        # Extract site_ids from metadata JSON
        running_site_ids = set()
        for row in records:
            if row and row[0]:
                import json
                try:
                    metadata = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    site_id = metadata.get('site_id')
                    if site_id:
                        running_site_ids.add(int(site_id))
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logging.warning(f"Could not parse metadata: {row[0]}, Error: {e}")

        logging.info(f"Found {len(running_site_ids)} sites with running inference jobs: {running_site_ids}")
        return running_site_ids

    @task
    def get_birdid_medium_visible_counts(sites):
        """Fetch BirdID-medium visible record counts (from max_confidence table) for each site"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        birdid_visible_counts = {}

        for site in sites:
            site_id = site["site_id"]
            query = f"""
            WITH tmp_record_ids AS (
                SELECT id
                FROM records
                WHERE site_id = {site_id}
            )
            SELECT count(distinct(mirmc.record_id))
            FROM model_inference_results_max_confidence AS mirmc
            WHERE mirmc.record_id = ANY (ARRAY(SELECT id FROM tmp_record_ids))
            AND model_id=3
            """

            # Execute query and fetch result
            result = postgres_hook.get_first(query)
            birdid_visible_counts[site_id] = result[0] if result else 0

        logging.info(f"Fetched BirdID Medium visible counts for {len(birdid_visible_counts)} sites")
        return birdid_visible_counts

    @task
    def get_skipped_record_counts(sites):
        """Fetch skipped record counts (records with errors excluding duration_mismatch) for each site"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        skipped_counts = {}

        for site in sites:
            site_id = site["site_id"]
            query = f"""
            SELECT COUNT(*)
            FROM records
            WHERE site_id = {site_id}
              AND errors IS NOT NULL
              AND errors != 'null'::jsonb
              AND errors::text NOT LIKE '%duration_mismatch%'
            """

            # Execute query and fetch result
            result = postgres_hook.get_first(query)
            skipped_counts[site_id] = result[0] if result else 0

        logging.info(f"Fetched skipped record counts for {len(skipped_counts)} sites")
        return skipped_counts

    @task
    def calculate_import_statuses(aggregated_data, record_counts, birdid_medium_counts, birdid_visible_counts, skipped_counts, running_jobs):
        """Calculate DB_IMPORT and BIRDID_MEDIUM statuses for each prefix"""
        # Handle empty input
        if not aggregated_data:
            logging.info("No aggregated data - no directories were processed")
            return []

        MAX_DIFF = 10  # acceptable difference between status "ready" and "ready with losses" and "pending"

        # Convert record_counts and birdid_medium_counts keys from strings to integers
        record_counts = {int(k): v for k, v in record_counts.items()}
        birdid_medium_counts = {int(k): v for k, v in birdid_medium_counts.items()}
        birdid_visible_counts = {int(k): v for k, v in birdid_visible_counts.items()}
        skipped_counts = {int(k): v for k, v in skipped_counts.items()}

        logging.info(f"Record counts: {record_counts}")
        logging.info(f"BirdID Medium processed counts: {birdid_medium_counts}")
        logging.info(f"BirdID Medium visible counts: {birdid_visible_counts}")
        logging.info(f"Skipped record counts: {skipped_counts}")
        logging.info(f"Running inference jobs for sites: {running_jobs}")

        enriched_rows = []

        for data in aggregated_data:
            site_id = data["site_id"]
            record_count = record_counts.get(site_id, 0) if site_id else 0
            birdid_medium_count = birdid_medium_counts.get(site_id, 0) if site_id else 0
            birdid_visible_count = birdid_visible_counts.get(site_id, 0) if site_id else 0
            skipped_count = skipped_counts.get(site_id, 0) if site_id else 0
            wav_count = data["wav_count"]

            # Calculate DB_IMPORT status
            if record_count == 0:
                db_import_status = ""
            else:
                diff = abs(wav_count - record_count)
                if diff == 0:
                    db_import_status = "ready"
                elif diff <= MAX_DIFF:
                    db_import_status = "ready with losses"
                else:
                    db_import_status = "pending"

            # Calculate BIRDID_MEDIUM status
            if record_count == 0:
                birdid_medium_status = ""
            elif site_id in running_jobs:
                birdid_medium_status = "running"
            else:
                # Calculate the expected processed count (processed + skipped)
                expected_processed = birdid_medium_count + skipped_count
                diff = abs(record_count - expected_processed)

                if diff == 0:
                    birdid_medium_status = "ready"
                elif diff <= MAX_DIFF:
                    birdid_medium_status = "ready with losses"
                else:
                    birdid_medium_status = "pending"

            logging.info(f"Prefix: {data['prefix']}, Site ID: {site_id}, WAV files: {wav_count}, Records: {record_count}, Skipped: {skipped_count}, BirdNET processed: {birdid_medium_count}, Status: {birdid_medium_status}")

            enriched_rows.append({
                "prefix": data["prefix"],
                "site_id": site_id,
                "wav_size_bytes": data["wav_size_bytes"],
                "wav_count": wav_count,
                "record_count": record_count,
                "skipped_records": skipped_count,
                "db_import": db_import_status,
                "birdid_medium_processed": birdid_medium_count,
                "birdid_medium": birdid_medium_status,
                "birdid_medium_visible": birdid_visible_count
            })

        return enriched_rows

    @task
    def transform_data(rows):
        # Handle empty input
        if not rows:
            logging.info("No data to transform - no directories were processed")
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df = df[["prefix", "site_id", "wav_size_bytes", "wav_count", "record_count", "skipped_records", "db_import", "birdid_medium_processed", "birdid_medium", "birdid_medium_visible"]]
        df = df.sort_values(by="prefix")
        return df

    @task
    def print_report(report_df):
        # Handle empty DataFrame
        if report_df.empty:
            logging.info("No new data to report - all directories up to date")
            return

        logging.info("File count report:")
        for index, row in report_df.iterrows():
            size_mb = row['wav_size_bytes'] / (1024 * 1024)
            site_info = f"{row['site_id']}" if pd.notna(row['site_id']) else "Unknown"
            db_import_status = row['db_import'] if row['db_import'] else "N/A"
            birdid_medium_status = row['birdid_medium'] if row['birdid_medium'] else "N/A"
            logging.info(f"Prefix: {row['prefix']}, Site ID: {site_info}, Size: {size_mb:.2f} MB, WAV files: {row['wav_count']}, Records: {row['record_count']}, Skipped: {row['skipped_records']}, DB Import: {db_import_status}, BirdId Medium processed: {row['birdid_medium_processed']}, BirdID Medium: {birdid_medium_status}, Visible in UI: {row['birdid_medium_visible']}")

    @task
    def create_report_table():
        """Create the report table if it doesn't exist"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        create_table_query = """
        CREATE TABLE IF NOT EXISTS workflow_reports (
            id SERIAL PRIMARY KEY,
            report_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            prefix VARCHAR(50) NOT NULL,
            site_id INTEGER,
            wav_size_bytes BIGINT,
            wav_count INTEGER,
            record_count INTEGER,
            skipped_records INTEGER,
            db_import VARCHAR(50),
            birdid_medium_processed INTEGER,
            birdid_medium VARCHAR(50),
            birdid_medium_visible INTEGER,
            visible_in_ui BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_site FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_workflow_reports_date ON workflow_reports(report_date);
        CREATE INDEX IF NOT EXISTS idx_workflow_reports_site_id ON workflow_reports(site_id);
        CREATE INDEX IF NOT EXISTS idx_workflow_reports_prefix ON workflow_reports(prefix);
        """

        postgres_hook.run(create_table_query)
        logging.info("Report table created or already exists")

    @task
    def save_report_to_db(report_df):
        """Save the report data to the database"""
        # Handle empty DataFrame - don't save if no data to report
        if report_df.empty:
            logging.info("No new data to save - skipping report creation (will show latest existing report)")
            return 0

        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        insert_query = """
        INSERT INTO workflow_reports (
            report_date, prefix, site_id, wav_size_bytes, wav_count,
            record_count, skipped_records, db_import, birdid_medium_processed, birdid_medium, birdid_medium_visible, visible_in_ui
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        report_date = datetime.now()
        rows_inserted = 0

        for index, row in report_df.iterrows():
            # Automatically set visible_in_ui based on birdid_medium status
            birdid_medium_status = row['birdid_medium'] if row['birdid_medium'] else ""
            visible_in_ui = birdid_medium_status in ["ready", "ready with losses"]

            values = (
                report_date,
                row['prefix'],
                int(row['site_id']) if pd.notna(row['site_id']) else None,
                int(row['wav_size_bytes']) if pd.notna(row['wav_size_bytes']) else None,
                int(row['wav_count']) if pd.notna(row['wav_count']) else None,
                int(row['record_count']) if pd.notna(row['record_count']) else None,
                int(row['skipped_records']) if pd.notna(row['skipped_records']) else None,
                row['db_import'] if row['db_import'] else None,
                int(row['birdid_medium_processed']) if pd.notna(row['birdid_medium_processed']) else None,
                row['birdid_medium'] if row['birdid_medium'] else None,
                int(row['birdid_medium_visible']) if pd.notna(row['birdid_medium_visible']) else None,
                visible_in_ui
            )

            postgres_hook.run(insert_query, parameters=values)
            rows_inserted += 1

        logging.info(f"Saved {rows_inserted} rows to workflow_reports table")
        return rows_inserted

    # Task dependencies
    sites = get_sites_from_db()
    create_report_table()
    last_report_dates = get_last_report_dates_by_directory()
    record_counts = get_record_counts_from_db(sites)
    birdid_medium_counts = get_birdid_medium_processed_counts(sites)
    birdid_visible_counts = get_birdid_medium_visible_counts(sites)
    skipped_counts = get_skipped_record_counts(sites)
    running_jobs = get_running_inference_jobs()
    directories = scan_directories()
    rows = list_wavs(directories, sites, last_report_dates)
    aggregated_data = aggregate_wav_data_by_prefix(rows, sites, last_report_dates)  # Added last_report_dates
    enriched_data = calculate_import_statuses(aggregated_data, record_counts, birdid_medium_counts, birdid_visible_counts, skipped_counts, running_jobs)
    report_df = transform_data(enriched_data)
    print_report(report_df)
    save_report_to_db(report_df)

create_report()