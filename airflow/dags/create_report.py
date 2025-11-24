import os
import pandas as pd
from airflow.decorators import dag, task
from datetime import datetime
import logging


@dag(
  dag_id='create_report',
  schedule='0 3 * * *',  # every day at 3:00
  start_date = datetime(year=2024, month=1, day=1, hour=9, minute=0),
  catchup=False,
)
def extract_data():

  @task
  def create_report():
    BASE_DIR = '/data'

    if not os.path.isdir(BASE_DIR):
      raise ValueError(f"Not a valid directory {BASE_DIR}")

    rows = []

    for root, dirs, files in os.walk(BASE_DIR):
      rel_path = os.path.relpath(root, BASE_DIR)
      # Calculate depth (how many levels deep we are)
      depth = rel_path.count(os.sep)

      # Only process directories at exactly depth 1
      if depth == 1:
        rows.append({
          "directory": rel_path,
          "files": files
        })

      # Prevent going deeper than 1 level
      if depth >= 1:
        dirs[:] = []

    return {"base_dir": BASE_DIR, "directories": rows}

  @task
  def list_wavs(data):
    rows = []

    for dir_info in data["directories"]:
      wav_count = sum(1 for f in dir_info["files"] if f.lower().endswith('.wav'))
      rows.append({
        "directory": dir_info["directory"],
        "wav_count": wav_count
      })
    return rows

  @task
  def transform_data(rows):
    df = pd.DataFrame(rows).sort_values(by="directory")
    return df

  @task
  def print_report(report_df):
    logging.info("File count report:")
    for index, row in report_df.iterrows():
      logging.info(f"Directory: {row['directory']}, WAV files: {row['wav_count']}")

  data = create_report()
  rows = list_wavs(data)
  report_df = transform_data(rows)
  print_report(report_df)

extract_data()
