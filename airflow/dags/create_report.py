import os
import pandas as pd
from airflow.decorators import dag, task
from datetime import datetime
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook

@dag(
  dag_id='create_report',
  schedule='0 3 * * *',  # every day at 3:00
  start_date = datetime(year=2024, month=1, day=1, hour=9, minute=0),
  catchup=False,
)
def extract_data():

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
  def get_birdnet_processed_counts(sites):
    """Fetch BirdNET-medium processed record counts for each site from the database"""
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

    birdnet_counts = {}

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
      birdnet_counts[site_id] = result[0] if result else 0

    logging.info(f"Fetched BirdNET processed counts for {len(birdnet_counts)} sites")
    return birdnet_counts

  @task
  def create_report():
    BASE_DIR = '/data'

    if not os.path.isdir(BASE_DIR):
      raise ValueError(f"Not a valid directory {BASE_DIR}")

    rows = []

    for root, dirs, files in os.walk(BASE_DIR):
      rel_path = os.path.relpath(root, BASE_DIR)
      depth = rel_path.count(os.sep)

      if depth == 1:
        rows.append({
          "directory": rel_path,
          "files": files,
          "root": root
        })

      if depth >= 1:
        dirs[:] = []

    return rows

  @task
  def list_wavs(rows):
    result = []

    for dir_info in rows:
      wav_count = sum(1 for f in dir_info["files"] if f.lower().endswith('.wav'))
      result.append({
        "directory": dir_info["directory"],
        "wav_count": wav_count,
        "root": dir_info["root"]
      })
    return result

  @task
  def calculate_wav_sizes(rows):
    enhanced_rows = []

    for row in rows:
      total_size = 0
      root_path = row["root"]

      for filename in os.listdir(root_path):
        if filename.lower().endswith('.wav'):
          file_path = os.path.join(root_path, filename)
          try:
            total_size += os.path.getsize(file_path)
          except OSError as e:
            logging.warning(f"Could not get size of {file_path}: {e}")

      enhanced_rows.append({
        "directory": row["directory"],
        "wav_count": row["wav_count"],
        "wav_size_bytes": total_size
      })

    return enhanced_rows

  @task
  def aggregate_wav_data_by_prefix(rows, sites):
    """Aggregate WAV file counts and sizes by prefix"""
    # Create a lookup dictionary from prefix to site_id
    prefix_to_site = {site["prefix"]: site["site_id"] for site in sites}

    # Dictionary to store aggregated data by prefix
    prefix_data = {}

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

    logging.info(f"Aggregated data for {len(prefix_data)} prefixes")
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
  def calculate_import_statuses(aggregated_data, record_counts, birdnet_counts, running_jobs):
      """Calculate DB_IMPORT and BIRDID_MEDIUM statuses for each prefix"""
      MAX_DIFF = 10

      # Convert record_counts and birdnet_counts keys from strings to integers
      record_counts = {int(k): v for k, v in record_counts.items()}
      birdnet_counts = {int(k): v for k, v in birdnet_counts.items()}

      logging.info(f"Record counts: {record_counts}")
      logging.info(f"BirdNET processed counts: {birdnet_counts}")
      logging.info(f"Running inference jobs for sites: {running_jobs}")

      enriched_rows = []

      for data in aggregated_data:
          site_id = data["site_id"]
          record_count = record_counts.get(site_id, 0) if site_id else 0
          birdnet_count = birdnet_counts.get(site_id, 0) if site_id else 0
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
                  db_import_status = "update this"

          # Calculate BIRDID_MEDIUM status
          if record_count == 0:
              birdid_medium_status = ""
          elif site_id in running_jobs:
              birdid_medium_status = "running"
          else:
              diff = abs(record_count - birdnet_count)
              if diff == 0:
                  birdid_medium_status = "ready"
              elif diff <= MAX_DIFF:
                  birdid_medium_status = "ready with losses"
              else:
                  birdid_medium_status = "update this"

          logging.info(f"Prefix: {data['prefix']}, Site ID: {site_id}, WAV files: {wav_count}, Records: {record_count}, BirdNET processed: {birdnet_count}, Status: {birdid_medium_status}")

          enriched_rows.append({
              "prefix": data["prefix"],
              "site_id": site_id,
              "wav_size_bytes": data["wav_size_bytes"],
              "wav_count": wav_count,
              "record_count": record_count,
              "db_import": db_import_status,
              "birdnet_processed": birdnet_count,
              "birdid_medium": birdid_medium_status
          })

      return enriched_rows

  @task
  def transform_data(rows):
    df = pd.DataFrame(rows)
    # Columns order: prefix, site_id, wav_size_bytes, wav_count, record_count, db_import, birdnet_processed, birdid_medium
    df = df[["prefix", "site_id", "wav_size_bytes", "wav_count", "record_count", "db_import", "birdnet_processed", "birdid_medium"]]
    df = df.sort_values(by="prefix")
    return df

  @task
  def print_report(report_df):
    logging.info("File count report:")
    for index, row in report_df.iterrows():
      size_mb = row['wav_size_bytes'] / (1024 * 1024)
      site_info = f"{row['site_id']}" if pd.notna(row['site_id']) else "Unknown"
      db_import_status = row['db_import'] if row['db_import'] else "N/A"
      birdid_medium_status = row['birdid_medium'] if row['birdid_medium'] else "N/A"
      logging.info(f"Prefix: {row['prefix']}, Site ID: {site_info}, Size: {size_mb:.2f} MB, WAV files: {row['wav_count']}, Records: {row['record_count']}, DB Import: {db_import_status}, BirdNET processed: {row['birdnet_processed']}, BirdID Medium: {birdid_medium_status}")

  # Task dependencies
  sites = get_sites_from_db()
  record_counts = get_record_counts_from_db(sites)
  birdnet_counts = get_birdnet_processed_counts(sites)
  running_jobs = get_running_inference_jobs()
  rows = create_report()
  rows = list_wavs(rows)
  rows = calculate_wav_sizes(rows)
  aggregated_data = aggregate_wav_data_by_prefix(rows, sites)
  enriched_data = calculate_import_statuses(aggregated_data, record_counts, birdnet_counts, running_jobs)
  report_df = transform_data(enriched_data)
  print_report(report_df)

extract_data()