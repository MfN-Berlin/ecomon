from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
}

dag = DAG(
    'postgres_weekly_backup',
    default_args=default_args,
    description='Weekly PostgreSQL backup with split chunks and rotation',
    schedule_interval='0 3 * * 0',  # Every Sunday at 03:00 AM
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
)

class NoTemplateBashOperator(BashOperator):
    template_fields = ()  # disables Jinja templating
with open("/opt/airflow/dags/scripts/backup_pg.sh") as f:
    bash_script = f.read()
backup_task = NoTemplateBashOperator(
    task_id='postgres_backup_task',
    bash_command=bash_script,
    dag=dag,
)
