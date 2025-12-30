from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Function to ensure the migration progress table and temporary results table exist and are cleared
def ensure_and_clear_tables():
    try:
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        # Ensure the migration progress table exists
        progress_table_query = """
        CREATE TABLE IF NOT EXISTS migration_progress (
            partition_name text PRIMARY KEY,
            processed_at timestamp DEFAULT now(),
            row_count bigint,
            duration_seconds integer
        );
        """
        postgres_hook.run(progress_table_query)

        # Recreate the temporary results table
        results_temp_table_query = """
        DROP TABLE IF EXISTS model_inference_results_max_confidence_temp;
        CREATE TABLE model_inference_results_max_confidence_temp (
            id bigint NOT NULL,
            record_id bigint NOT NULL,
            model_id integer NOT NULL,
            label_id integer NOT NULL,
            start_time numeric(9,4) NOT NULL,
            end_time numeric(9,4) NOT NULL,
            confidence real NOT NULL,
            PRIMARY KEY (record_id, label_id, model_id)
        );
        """
        postgres_hook.run(results_temp_table_query)

        print("Migration progress table ensured and temporary results table cleared.")
    except Exception as e:
        print(f"Error ensuring tables: {e}")
        raise

# Function to summarize the migration using the migration progress table
def summarize_migration():
    try:
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        query = """
        SELECT partition_name, row_count, duration_seconds, processed_at
        FROM migration_progress
        ORDER BY processed_at DESC
        LIMIT 10;
        """
        records = postgres_hook.get_records(query)
        print("Migration Summary:")
        for record in records:
            print(record)
    except Exception as e:
        print(f"Error summarizing migration: {e}")
        raise

def process_all_partitions(progress_table, results_temp_table, statement_timeout):
    try:
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        for i in range(1, 201):
            partition_name = f"mir_partitions.model_inference_results_p{i:03d}"

            try:
                # Get the current row count for the partition
                row_count_query = f"SELECT count(*) FROM {partition_name};"
                current_row_count = postgres_hook.get_first(row_count_query)
                if not current_row_count or not isinstance(current_row_count[0], int):
                    print(f"✗ Failed to fetch row count for {partition_name}.")
                    continue

                current_row_count = current_row_count[0]

                # Check if the partition has new data
                last_processed_query = f"""
                SELECT row_count FROM {progress_table} WHERE partition_name = %s;
                """
                last_processed = postgres_hook.get_first(last_processed_query, parameters=(partition_name,))
                if last_processed and current_row_count <= last_processed[0]:
                    print(f"✓ {partition_name} has no new data. Skipping.")
                    continue

                print(f"→ Processing partition: {partition_name} ({current_row_count} rows)")

                # Measure the start time
                start_time = datetime.now()

                # Start processing the partition
                migration_query = f"""
                SET statement_timeout = '{statement_timeout}s';
                SET work_mem = '1GB';
                SET temp_buffers = '512MB';

                BEGIN;

                WITH best AS (
                    SELECT record_id, label_id, model_id, MAX(confidence) AS max_confidence
                    FROM {partition_name}
                    GROUP BY record_id, label_id, model_id
                ),
                dedup AS (
                    SELECT p.record_id, p.label_id, p.model_id, p.id, p.start_time, p.end_time, p.confidence
                    FROM {partition_name} p
                    JOIN best b
                    ON p.record_id = b.record_id
                    AND p.label_id  = b.label_id
                    AND p.model_id  = b.model_id
                    AND p.confidence = b.max_confidence
                )
                INSERT INTO {results_temp_table}
                (record_id, label_id, model_id, id, start_time, end_time, confidence)
                SELECT record_id, label_id, model_id, id, start_time, end_time, confidence
                FROM dedup
                ON CONFLICT (record_id, label_id, model_id)
                DO UPDATE SET
                    id = EXCLUDED.id,
                    start_time = EXCLUDED.start_time,
                    end_time = EXCLUDED.end_time,
                    confidence = EXCLUDED.confidence
                WHERE EXCLUDED.confidence > {results_temp_table}.confidence;

                COMMIT;
                """
                postgres_hook.run(migration_query)

                # Measure the end time and calculate the duration
                end_time = datetime.now()
                duration_seconds = (end_time - start_time).total_seconds()

                # Update the progress table with the duration
                progress_update_query = f"""
                INSERT INTO {progress_table}(partition_name, row_count, duration_seconds)
                VALUES (%s, %s, %s)
                ON CONFLICT (partition_name)
                DO UPDATE SET
                    row_count = EXCLUDED.row_count,
                    duration_seconds = EXCLUDED.duration_seconds,
                    processed_at = now();
                """
                postgres_hook.run(progress_update_query, parameters=(partition_name, current_row_count, duration_seconds))

                print(f"✓ Finished processing partition: {partition_name} in {duration_seconds:.2f} seconds")

            except Exception as e:
                print(f"✗ FAILED processing partition: {partition_name} - {str(e)}")
                continue  # Skip to the next partition

    except Exception as e:
        print(f"✗ FAILED processing partitions - {str(e)}")
        raise

# Define the DAG
with DAG(
    'Populate_Max_Table_Test',
    default_args=default_args,
    description='Test Populate max table from partitioned data using a temporary table',
    schedule_interval='0 4 * * 1-5',  # Run at 4:00 AM, Monday to Friday
    start_date=datetime(2025, 12, 30),
    catchup=False,
) as dag:

    # Task 1: Ensure and clear the migration progress table and temporary results table
    ensure_tables_task = PythonOperator(
        task_id='ensure_and_clear_tables',
        python_callable=ensure_and_clear_tables,
    )

    # Task 2: Process all partitions sequentially
    process_partitions_task = PythonOperator(
        task_id='process_all_partitions',
        python_callable=process_all_partitions,
        op_kwargs={
            'progress_table': 'migration_progress',
            'results_temp_table': 'model_inference_results_max_confidence_temp',
            'statement_timeout': 3600,
        },
    )

    # Task 3: Summarize the migration using the migration progress table
    summarize_task = PythonOperator(
        task_id='summarize_migration',
        python_callable=summarize_migration,
    )

    # Set task dependencies
    ensure_tables_task >> process_partitions_task >> summarize_task