import logging
from airflow.decorators import dag, task
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
import json
import os

API_URL = os.environ.get("API_URL", "").strip()
API_VERIFY_SSL = os.environ.get("API_VERIFY_SSL", "true").strip().lower() not in {"0", "false", "no"}

@dag(
    dag_id='run_inferences',
    schedule="0 21 * * 1-5",  # 21:00 on weekdays (Monday=1 through Friday=5)
    start_date=datetime(2025, 12, 1),
    catchup=False,
)
def run_inferences():

    @task
    def check_report_table_exists():
        """Check if the workflow_reports table exists"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'workflow_reports'
        );
        """

        result = postgres_hook.get_first(query)
        table_exists = result[0] if result else False
        logging.info(f"Workflow reports table exists: {table_exists}")
        return table_exists

    @task
    def check_running_inference_jobs():
        """Check if there are any running inference jobs"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        query = """
        SELECT COUNT(*)
        FROM jobs
        WHERE status='running' AND topic='model_inference_site';
        """

        result = postgres_hook.get_first(query)
        running_jobs = result[0] if result else 0
        logging.info(f"Running inference jobs: {running_jobs}")
        return running_jobs > 0

    @task
    def get_models_needing_processing():
        """Find models with pending or partial status"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        query = """
        SELECT
            site_id,
            model_id,
            record_count,
            model_processed,
            skipped_records,
            model_status,
            (record_count - model_processed - skipped_records) as records_to_process
        FROM workflow_reports
        WHERE model_status IN ('pending', 'partial')
        AND report_date = (SELECT MAX(report_date) FROM workflow_reports)
        ORDER BY records_to_process DESC
        LIMIT 4;  -- Number of models to process in this DAG run. Adjust based on desired workload.
        """

        records = postgres_hook.get_records(query)
        if not records:
            logging.info("No models found needing processing")
            return []

        models = []
        for record in records:
            models.append({
                'site_id': record[0],
                'model_id': record[1],
                'records_to_process': record[6]
            })
            logging.info(f"Site {record[0]}, Model '{record[1]}': {record[6]} records to process")

        return models

    @task
    def trigger_inference_job(model_info):
        """Trigger an inference job via direct POST request"""
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        # Get model ID
        model_id = model_info['model_id']

        # Set date range (last 6 months)
        end_datetime = datetime.now().isoformat()
        start_datetime = (datetime.now() - timedelta(days=180)).isoformat()

        # Get actual date range if available
        query = f"""
        SELECT MIN(record_datetime), MAX(record_datetime)
        FROM records
        WHERE site_id = {model_info['site_id']}
        """
        result = postgres_hook.get_first(query)
        if result and result[0] and result[1]:
            start_datetime = result[0].isoformat()
            end_datetime = result[1].isoformat()

        # Prepare the request
        payload = {
            "operationName": "inferenceSiteTimespan",
            "query": """
                mutation inferenceSiteTimespan($modelId: Int!, $siteId: Int!, $startDatetime: String!, $endDatetime: String!) {
                  data: inferenceSiteTimespan(
                    inferenceSiteRequestInput: {modelId: $modelId, siteId: $siteId, startDatetime: $startDatetime, endDatetime: $endDatetime}
                  ) {
                    jobId
                  }
                }
            """,
            "variables": {
                "siteId": model_info['site_id'],
                "modelId": model_id,
                "startDatetime": start_datetime,
                "endDatetime": end_datetime
            }
        }

        logging.info("Inference payload: %s", json.dumps(payload, default=str))

        # Make the POST request
        if not API_URL:
            raise ValueError("API_URL is not set. Ensure it is provided via docker-compose.yaml environment variables.")
        headers = {"Content-Type": "application/json"}
        if API_URL.startswith("https://") and not API_VERIFY_SSL:
            logging.warning("API_VERIFY_SSL is disabled; TLS certificates will not be verified for API_URL.")
        response = requests.post(API_URL, json=payload, headers=headers, verify=API_VERIFY_SSL)

        if response.status_code == 200:
            job_id = response.json().get('data', {}).get('data', {}).get('jobId')
            logging.info(f"Successfully triggered job {job_id} for site {model_info['site_id']}, model {model_info['model_id']}")
            return job_id
        else:
            logging.error(f"Failed to trigger job. Status: {response.status_code}, Response: {response.text}")
            return None

    from airflow.operators.python import BranchPythonOperator
    from airflow.utils.trigger_rule import TriggerRule

    def should_continue(has_running_jobs):
        if has_running_jobs:
            return 'skip_remaining_tasks'
        return 'get_models_needing_processing'

    @task(trigger_rule=TriggerRule.NONE_FAILED)
    def skip_remaining_tasks():
        logging.info("Skipping inference jobs as there are already running jobs")
        return []

    # Set up task flow
    table_exists = check_report_table_exists()
    has_running_jobs = check_running_inference_jobs()

    # if there are running inference jobs, the rest of the DAG is skipped
    # to avoid overloading the system. Otherwise, it continues to check for models
    # needing processing and triggers inference jobs as needed.
    branch = BranchPythonOperator(
        task_id='should_continue',
        python_callable=should_continue,
        op_kwargs={'has_running_jobs': '{{ task_instance.xcom_pull(task_ids="check_running_inference_jobs") }}'}
    )
    skip_task = skip_remaining_tasks()
    models = get_models_needing_processing()

    table_exists >> has_running_jobs >> branch
    branch >> [skip_task, models]
    models >> trigger_inference_job.expand(model_info=models)

run_inferences()