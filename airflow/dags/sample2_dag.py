from airflow.decorators import dag, task
from datetime import datetime
import pandas as pd
import logging

@dag(
  dag_id = 'weather_etl2',
  start_date = datetime(year=2024, month=1, day=1, hour=9, minute=0),
  schedule = '@daily',
  catchup = True,
  max_active_runs = 1
)
def weather_etl():

  @task
  def extract_data():
    logging.info("Extracting data...")
    return {
      "date": "2024-01-01",
      "location": "Berlin",
      "weather": {
          "temp": -2,
          "conditions": "Light snow and some wind"
      }
    }

  @task
  def transform_data(raw_data):
    transformed_data = [
        [
          raw_data.get("date"),
          raw_data.get("location"),
          raw_data.get("weather").get("temp"),
          raw_data.get("weather").get("conditions")
        ]
    ]
    return transformed_data

  @task
  def load_data(transformed_data):
    loaded_data = pd.DataFrame(transformed_data)
    loaded_data.columns=["date", "location", "weather_temp", "weather_conditions"]
    logging.info(f"Loaded data:\n{loaded_data.to_string()}")

  raw_data = extract_data()
  transformed_data = transform_data(raw_data)
  load_data(transformed_data)

weather_etl()
