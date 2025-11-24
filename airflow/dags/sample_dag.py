from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
import logging
import pandas as pd


with DAG(
    dag_id='weather_etl',
    start_date=datetime(year=2024, month=1, day=1, hour=9, minute=0),
    schedule='@daily',
    catchup=False,
    max_active_runs=1,
    render_template_as_native_obj=True
) as dag:
  def extract_data_callable():
      logging.info("Extracting data...")
      return {
        "date": "2024-01-01",
        "location": "Berlin",
        "weather": {
            "temp": -2,
            "conditions": "Light snow and some wind"
        }
      }

  extract_data = PythonOperator(
    dag=dag,
    task_id="extract_data",
    python_callable=extract_data_callable
  )

  def transform_data_callable(raw_data):
    transformed_data = [
        [
          raw_data.get("date"),
          raw_data.get("location"),
          raw_data.get("weather").get("temp"),
          raw_data.get("weather").get("conditions")
        ]
    ]
    return transformed_data

  transform_data = PythonOperator(
    dag=dag,
    task_id="transform_data",
    python_callable=transform_data_callable,
    op_kwargs={"raw_data": "{{ ti.xcom_pull(task_ids='extract_data') }}"}
  )

  def load_data_callable(transformed_data):
    loaded_data = pd.DataFrame(transformed_data)
    loaded_data.columns=["date", "location", "weather_temp", "weather_conditions"]
    logging.info(f"Loaded data:\n{loaded_data.to_string()}")

  load_data = PythonOperator(
    dag=dag,
    task_id="load_data",
    python_callable=load_data_callable,
    op_kwargs={"transformed_data": "{{ ti.xcom_pull(task_ids='transform_data') }}"}
  )

  extract_data >> transform_data >> load_data