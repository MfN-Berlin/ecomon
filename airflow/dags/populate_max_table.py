from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

# Custom BashOperator to disable Jinja templating
class NoTemplateBashOperator(BashOperator):
    template_fields = ()  # Disable Jinja templating

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Inline function to ensure the temporary migration progress table exists
def ensure_migration_progress_temp_table():
    import subprocess
    command = f"""
    docker exec my_db_container psql -U {os.getenv('PG_USER')} -d {os.getenv('PG_DATABASE')} -h {os.getenv('PG_HOST')} -p {os.getenv('PG_PORT')} -c "
    CREATE TABLE IF NOT EXISTS migration_progress_temp (
        partition_name text PRIMARY KEY,
        processed_at timestamp DEFAULT now(),
        row_count bigint,
        duration_seconds integer
    );
    "
    """
    subprocess.run(command, shell=True, check=True)

# Inline function to summarize the migration using the temporary table
def summarize_migration_temp():
    import subprocess
    command = f"""
    docker exec my_db_container psql -U {os.getenv('PG_USER')} -d {os.getenv('PG_DATABASE')} -h {os.getenv('PG_HOST')} -p {os.getenv('PG_PORT')} -c "
    SELECT partition_name, row_count, duration_seconds, processed_at
    FROM migration_progress_temp
    ORDER BY processed_at DESC
    LIMIT 10;
    "
    """
    subprocess.run(command, shell=True, check=True)

# Load the process_partition.sh script
with open("/opt/airflow/dags/scripts/populate_max_table_from_partition.sh") as f:
    process_partition_script = f.read()

# Define the DAG
with DAG(
    'Populate_Max_Table_Test',
    default_args=default_args,
    description='Test Populate max table from partitioned data using a temporary table',
    schedule_interval='0 4 * * 1-5',  # Run at 4:00 AM, Monday to Friday
    start_date=datetime(2025, 12, 30),
    catchup=False,
) as dag:

    # Task 1: Ensure temporary migration progress table exists
    ensure_table_task = PythonOperator(
        task_id='ensure_migration_progress_temp_table',
        python_callable=ensure_migration_progress_temp_table,
    )

    # Task 2: Process each partition sequentially
    previous_task = ensure_table_task
    for i in range(1, 201):
        partition_name = f"mir_partitions.model_inference_results_p{i:03d}"
        process_partition_task = NoTemplateBashOperator(
            task_id=f'process_partition_{i:03d}',
            bash_command=process_partition_script,
            env={
                'CONTAINER': 'my_db_container',
                'PG_USER': os.getenv('PG_USER'),
                'PG_PASSWORD': os.getenv('PG_PASSWORD'),
                'PG_HOST': os.getenv('PG_HOST'),
                'PG_PORT': os.getenv('PG_PORT'),
                'PG_DATABASE': os.getenv('PG_DATABASE'),
                'LOGDIR': './migrate_logs',
                'STATEMENT_TIMEOUT': '3600',
                'PARTITION_NAME': partition_name,
                'PROGRESS_TABLE': 'migration_progress_temp',  # Use the temporary table
            },
        )
        # Set sequential dependency
        previous_task >> process_partition_task
        previous_task = process_partition_task

    # Task 3: Summarize the migration using the temporary table
    summarize_task = PythonOperator(
        task_id='summarize_migration_temp',
        python_callable=summarize_migration_temp,
    )

    # Set final dependency
    previous_task >> summarize_task