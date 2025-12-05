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

# Task 1: Create backup (read from file)
with open("/opt/airflow/dags/scripts/backup_pg.sh") as f:
    backup_script = f.read()

create_backup = NoTemplateBashOperator(
    task_id='postgres_backup_task',
    bash_command=backup_script,
    dag=dag,
)

# Task 2: Compress backup
compress_backup = NoTemplateBashOperator(
    task_id='compress_backup',
    bash_command="""
set -euo pipefail

TIMESTAMP=$(cat /backup/current_timestamp.txt)
BACKUP_BASENAME="basebackup_$TIMESTAMP"
BACKUP_PATH="/backup/$BACKUP_BASENAME"
BACKUP_TAR="/backup/$BACKUP_BASENAME.tar.gz"

echo "Compressing backup: $BACKUP_BASENAME"
tar -C "/backup" -czf "$BACKUP_TAR" "$BACKUP_BASENAME"

echo "Removing uncompressed backup directory..."
rm -rf "$BACKUP_PATH"

echo "Backup compressed: $BACKUP_TAR"
    """,
    dag=dag,
)

# Task 3: Rotate old backups
rotate_backups = NoTemplateBashOperator(
    task_id='rotate_backups',
    bash_command="""
set -euo pipefail

echo "Rotating old backups (keeping $MAX_BACKUPS)..."

ALL_BACKUPS=($(ls -1t /backup/basebackup_*.tar.gz 2>/dev/null || true))

COUNT=${#ALL_BACKUPS[@]}

if (( COUNT > MAX_BACKUPS )); then
    DELETE_COUNT=$((COUNT - MAX_BACKUPS))
    echo "Removing $DELETE_COUNT oldest backups"

    for ((i=MAX_BACKUPS; i<COUNT; i++)); do
        OLD="${ALL_BACKUPS[$i]}"
        echo "Deleting: $OLD"
        rm -f "$OLD"
    done
else
    echo "No old backups to remove. Current count: $COUNT"
fi

rm -f /backup/current_timestamp.txt

echo "Backup rotation complete"
    """,
    dag=dag,
)

# Define task dependencies
create_backup >> compress_backup >> rotate_backups