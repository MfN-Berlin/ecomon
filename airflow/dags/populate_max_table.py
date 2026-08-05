#**************************************
# Description: Airflow DAG to populate the
# max confidence table from partitioned data.
# Used in the Dashboard page.
# See docs/automation.md for details
#**************************************

from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import dag
from datetime import datetime, timedelta
import time

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'min_confidence': 0.1,
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

        # Create the temporary results table if it doesn't exist (don't drop it)
        results_temp_table_query = """
        CREATE TABLE IF NOT EXISTS model_inference_results_max_confidence_temp (
            id bigint NOT NULL,
            record_id bigint NOT NULL,
            model_id integer NOT NULL,
            label_id integer NOT NULL,
            start_time numeric(9,4) NOT NULL,
            end_time numeric(9,4) NOT NULL,
            confidence real NOT NULL,
            PRIMARY KEY (record_id, label_id, model_id)
        );

        -- Create indexes if they don't exist
        CREATE INDEX IF NOT EXISTS idx_mir_max_conf_temp_compound
        ON model_inference_results_max_confidence_temp (model_id, label_id, confidence DESC, record_id);

        CREATE INDEX IF NOT EXISTS idx_mir_max_conf_temp_label
        ON model_inference_results_max_confidence_temp (label_id, confidence DESC);

        CREATE INDEX IF NOT EXISTS idx_mir_max_conf_temp_model
        ON model_inference_results_max_confidence_temp (model_id);
        """
        postgres_hook.run(results_temp_table_query)

        print("Migration progress table and temporary results table ensured.")
    except Exception as e:
        print(f"Error ensuring tables: {e}")
        raise

# Function to summarize the migration using the migration progress table
def summarize_migration():
    try:
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        # Query to calculate the summary statistics
        summary_query = """
        SELECT
            COUNT(*) AS partitions_processed,  -- Total number of partitions processed
            SUM(row_count) AS total_rows,      -- Total number of rows processed
            MAX(duration_seconds) AS longest_duration,  -- Longest processing time
            MIN(duration_seconds) AS shortest_duration, -- Shortest processing time
            AVG(duration_seconds) AS average_duration   -- Average processing time
        FROM migration_progress;
        """

        # Fetch the summary statistics
        summary = postgres_hook.get_first(summary_query)

        # Print the summary statistics
        print("Migration Summary:")
        print(f"Partitions Processed: {summary[0]}")
        print(f"Total Rows Processed: {summary[1]}")
        print(f"Longest Duration: {summary[2]} seconds")
        print(f"Shortest Duration: {summary[3]} seconds")
        avg_duration = summary[4] if summary[4] is not None else 0
        print(f"Average Duration: {avg_duration:.2f} seconds")

    except Exception as e:
        print(f"Error summarizing migration: {e}")
        raise

# Function to get partition row count
def get_partition_row_count(postgres_hook, partition_name):
    """Get the row count for a partition"""
    try:
        row_count_query = f"SELECT count(*) FROM {partition_name};"
        current_row_count = postgres_hook.get_first(row_count_query)
        if not current_row_count or not isinstance(current_row_count[0], int):
            return None
        return current_row_count[0]
    except Exception as e:
        print(f"✗ Failed to fetch row count for {partition_name}: {str(e)}")
        return None

# Function to check if partition needs processing
def should_process_partition(postgres_hook, partition_name, current_row_count, progress_table):
    """Check if partition has new data and needs processing"""
    try:
        last_processed_query = f"""
        SELECT row_count FROM {progress_table} WHERE partition_name = %s;
        """
        last_processed = postgres_hook.get_first(last_processed_query, parameters=(partition_name,))

        if last_processed and current_row_count <= last_processed[0]:
            print(f"✓ {partition_name} has no new data. Skipping.")
            return False
        return True
    except Exception as e:
        print(f"✗ Failed to check partition status for {partition_name}: {str(e)}")
        return False

# Function to process a single partition
def process_partition_data(postgres_hook, partition_name, results_temp_table, statement_timeout):
    """Process the data for a single partition"""
    # Use reduced memory settings to prevent OOM kills
    migration_query = f"""
    SET statement_timeout = '{statement_timeout}s';
    SET work_mem = '256MB';
    SET temp_buffers = '128MB';

    BEGIN;

    WITH ranked_rows AS (
        SELECT record_id, label_id, model_id, id, start_time, end_time, confidence,
               ROW_NUMBER() OVER (
                   PARTITION BY record_id, label_id, model_id
                   ORDER BY confidence DESC, id ASC
               ) AS rank
        FROM {partition_name}
    )
    INSERT INTO {results_temp_table}
    (record_id, label_id, model_id, id, start_time, end_time, confidence)
    SELECT record_id, label_id, model_id, id, start_time, end_time, confidence
    FROM ranked_rows
    WHERE rank = 1  -- Select only the row with the highest confidence
    ON CONFLICT (record_id, label_id, model_id)
    DO UPDATE SET
        id = EXCLUDED.id,
        start_time = EXCLUDED.start_time,
        end_time = EXCLUDED.end_time,
        confidence = EXCLUDED.confidence;

    COMMIT;
    """
    postgres_hook.run(migration_query)

# Function to update progress table
def update_partition_progress(postgres_hook, partition_name, current_row_count, duration_seconds, progress_table):
    """Update the progress table with partition processing results"""
    print(f"→ Updating progress table for {partition_name} (rows: {current_row_count}, duration: {duration_seconds:.2f}s)")

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

# Function to process a single partition (wrapper)
def process_single_partition(postgres_hook, partition_name, progress_table, results_temp_table, statement_timeout):
    """Process a single partition with all checks and updates"""
    try:
        # Get row count
        current_row_count = get_partition_row_count(postgres_hook, partition_name)
        if current_row_count is None:
            return False

        # Check if processing is needed
        if not should_process_partition(postgres_hook, partition_name, current_row_count, progress_table):
            return True

        print(f"→ Processing partition: {partition_name} ({current_row_count} rows)")

        # Measure the start time
        start_time = datetime.now()

        # Process the partition data
        process_partition_data(postgres_hook, partition_name, results_temp_table, statement_timeout)

        # Measure the end time and calculate the duration
        end_time = datetime.now()
        duration_seconds = (end_time - start_time).total_seconds()

        # Update progress table
        update_partition_progress(postgres_hook, partition_name, current_row_count, duration_seconds, progress_table)

        print(f"✓ Finished processing partition: {partition_name} in {duration_seconds:.2f} seconds")
        return True

    except Exception as e:
        print(f"✗ FAILED processing partition: {partition_name} - {str(e)}")
        return False

# Main function to process all partitions
def process_all_partitions(progress_table, results_temp_table, statement_timeout):
    """Process all partitions sequentially with index management"""
    try:
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        # Drop indexes before processing for faster INSERT performance
        print("Dropping indexes for faster data loading...")
        drop_indexes_query = f"""
        DROP INDEX IF EXISTS idx_mir_max_conf_temp_compound;
        DROP INDEX IF EXISTS idx_mir_max_conf_temp_label;
        DROP INDEX IF EXISTS idx_mir_max_conf_temp_model;
        """
        postgres_hook.run(drop_indexes_query)

        processed_count = 0
        failed_count = 0

        for i in range(1, 501):
            partition_name = f"mir_partitions.model_inference_results_p{i:03d}"

            success = process_single_partition(
                postgres_hook,
                partition_name,
                progress_table,
                results_temp_table,
                statement_timeout
            )

            if success:
                processed_count += 1
            else:
                failed_count += 1

        # Recreate indexes after all partitions are processed
        print("Recreating indexes...")
        recreate_indexes_query = f"""
        CREATE INDEX idx_mir_max_conf_temp_compound 
        ON {results_temp_table} (model_id, label_id, confidence DESC, record_id);
        
        CREATE INDEX idx_mir_max_conf_temp_label 
        ON {results_temp_table} (label_id, confidence DESC);
        
        CREATE INDEX idx_mir_max_conf_temp_model 
        ON {results_temp_table} (model_id);
        """
        postgres_hook.run(recreate_indexes_query)

        print(f"✓ Processing complete. Processed: {processed_count}, Failed: {failed_count}")

    except Exception as e:
        print(f"✗ FAILED processing partitions - {str(e)}")
        raise

def remove_low_confidence_inferences(results_temp_table, min_confidence):
    """Remove inferences with confidence below min_confidence + 0.1"""
    try:
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
        threshold = min_confidence + 0.1
        delete_query = f"""
        DELETE FROM {results_temp_table}
        WHERE confidence < %s;
        """
        postgres_hook.run(delete_query, parameters=(threshold,))
        print(f"✓ Removed inferences with confidence below {threshold}")
    except Exception as e:
        print(f"✗ Failed to remove low confidence inferences: {e}")
        raise


def swap_tables():
    """Merge temp table data into main table, preserving existing data"""
    try:
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        # Check if main table exists
        check_main_table = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'model_inference_results_max_confidence'
        );
        """
        main_table_exists = postgres_hook.get_first(check_main_table)[0]

        if main_table_exists:
            merge_query = """
            SET work_mem = '512MB';
            SET maintenance_work_mem = '1GB';

            BEGIN;

            -- Drop indexes
            DROP INDEX IF EXISTS idx_mir_max_conf_compound;
            DROP INDEX IF EXISTS idx_mir_max_conf_label;
            DROP INDEX IF EXISTS idx_mir_max_conf_model;

            -- Fast merge without index overhead
            INSERT INTO model_inference_results_max_confidence
            (id, record_id, model_id, label_id, start_time, end_time, confidence)
            SELECT id, record_id, model_id, label_id, start_time, end_time, confidence
            FROM model_inference_results_max_confidence_temp
            ON CONFLICT (record_id, label_id, model_id)
            DO UPDATE SET
                id = EXCLUDED.id,
                start_time = EXCLUDED.start_time,
                end_time = EXCLUDED.end_time,
                confidence = EXCLUDED.confidence;

            -- Recreate indexes (parallel build if possible)
            CREATE INDEX idx_mir_max_conf_compound
            ON model_inference_results_max_confidence (model_id, label_id, confidence DESC, record_id);

            CREATE INDEX idx_mir_max_conf_label
            ON model_inference_results_max_confidence (label_id, confidence DESC);

            CREATE INDEX idx_mir_max_conf_model
            ON model_inference_results_max_confidence (model_id);

            COMMIT;
            """
            postgres_hook.run(merge_query)
            print("✓ Data merged from temp to main table")
        else:
            # First run - rename temp to main
            first_run_query = """
            BEGIN;

            -- Rename temp table to main (first run)
            ALTER TABLE model_inference_results_max_confidence_temp
            RENAME TO model_inference_results_max_confidence;

            -- Create new empty temp table for next run
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

            -- Create indexes on new temp table
            CREATE INDEX idx_mir_max_conf_temp_compound
            ON model_inference_results_max_confidence_temp (model_id, label_id, confidence DESC, record_id);

            CREATE INDEX idx_mir_max_conf_temp_label
            ON model_inference_results_max_confidence_temp (label_id, confidence DESC);

            CREATE INDEX idx_mir_max_conf_temp_model
            ON model_inference_results_max_confidence_temp (model_id);

            COMMIT;
            """
            postgres_hook.run(first_run_query)
            print("✓ First run: Promoted temp table to main table")

    except Exception as e:
        print(f"✗ Failed to merge tables: {e}")
        raise

# Define the DAG
@dag(
    dag_id='Populate_Max_Table',
    default_args=default_args,
    description='Populate max table from partitioned data using a temporary table',
    schedule_interval='0 5 * * 1-5',  # Run at 5:00 AM, Monday to Friday
    start_date=datetime(2025, 12, 30),
    catchup=False,
    tags=['dashboard', 'etl'],
)
def populate_max_table_dag():

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

    # Task 2.5: Remove low confidence inferences
    remove_low_conf_task = PythonOperator(
        task_id='remove_low_confidence_inferences',
        python_callable=remove_low_confidence_inferences,
        op_kwargs={
            'results_temp_table': 'model_inference_results_max_confidence_temp',
            'min_confidence': default_args['min_confidence'],
        },
    )

    # Task 3: Summarize the migration using the migration progress table
    summarize_task = PythonOperator(
        task_id='summarize_migration',
        python_callable=summarize_migration,
    )

    # Task 4: Swap the tables
    swap_tables_task = PythonOperator(
        task_id='swap_tables',
        python_callable=swap_tables,
    )

    # Set task dependencies
    ensure_tables_task >> process_partitions_task >> remove_low_conf_task >> summarize_task >> swap_tables_task

# This is required for the decorator to work
populate_max_table_dag()
