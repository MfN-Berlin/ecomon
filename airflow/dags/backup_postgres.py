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

# Task 3: Verify backup integrity
verify_backup = NoTemplateBashOperator(
    task_id='verify_backup',
    bash_command="""
set -euo pipefail

TIMESTAMP=$(cat /backup/current_timestamp.txt)
BACKUP_TAR="/backup/basebackup_$TIMESTAMP.tar.gz"

echo "=== Backup Integrity Verification ==="
echo "Archive: $BACKUP_TAR"
echo ""

# Check 1: File exists
if [ ! -f "$BACKUP_TAR" ]; then
    echo "ERROR: Backup file does not exist!"
    exit 1
fi
echo "✓ Backup file exists"

# Check 2: File is not empty
FILE_SIZE=$(stat -f%z "$BACKUP_TAR" 2>/dev/null || stat -c%s "$BACKUP_TAR" 2>/dev/null)
if [ "$FILE_SIZE" -eq 0 ]; then
    echo "ERROR: Backup file is empty!"
    exit 1
fi
echo "✓ Backup file is not empty (Size: $(numfmt --to=iec-i --suffix=B $FILE_SIZE 2>/dev/null || echo ${FILE_SIZE} bytes))"

# Check 3: File has minimum expected size (100MB)
MIN_SIZE=$((100 * 1024 * 1024))  # 100MB in bytes
if [ "$FILE_SIZE" -lt "$MIN_SIZE" ]; then
    echo "WARNING: Backup file is smaller than expected minimum (100MB)"
    echo "Current size: $(numfmt --to=iec-i --suffix=B $FILE_SIZE 2>/dev/null || echo ${FILE_SIZE} bytes)"
fi

# Check 4: Verify gzip integrity
echo "Checking gzip integrity..."
if ! gzip -t "$BACKUP_TAR" 2>&1; then
    echo "ERROR: Gzip integrity check failed!"
    exit 1
fi
echo "✓ Gzip compression is valid"

# Check 5: Test tar archive without extracting
echo "Testing tar archive structure..."
if ! tar -tzf "$BACKUP_TAR" > /dev/null 2>&1; then
    echo "ERROR: Tar archive test failed!"
    exit 1
fi
echo "✓ Tar archive structure is valid"

# Check 6: Verify essential PostgreSQL files are present
echo "Checking for essential PostgreSQL files..."
REQUIRED_FILES=("PG_VERSION" "postgresql.conf" "pg_hba.conf")
MISSING_FILES=()

# Disable pipefail temporarily to avoid SIGPIPE from grep -q
set +o pipefail
for file in "${REQUIRED_FILES[@]}"; do
    if tar -tzf "$BACKUP_TAR" 2>/dev/null | grep -q "/${file}\$"; then
        : # File found, do nothing
    else
        MISSING_FILES+=("$file")
    fi
done
set -o pipefail

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "WARNING: Some expected PostgreSQL files are missing:"
    printf '  - %s\n' "${MISSING_FILES[@]}"
else
    echo "✓ All essential PostgreSQL files present"
fi

# Check 7: Count files in archive
set +o pipefail
FILE_COUNT=$(tar -tzf "$BACKUP_TAR" 2>/dev/null | wc -l)
set -o pipefail
echo "✓ Archive contains $FILE_COUNT files/directories"

# Check 8: Check for base directory
echo "Verifying backup base directory..."
BACKUP_BASENAME="basebackup_$TIMESTAMP"
set +o pipefail
FIRST_ENTRY=$(tar -tzf "$BACKUP_TAR" 2>/dev/null | { read line; echo "$line"; })
set -o pipefail

if [[ "$FIRST_ENTRY" != "$BACKUP_BASENAME/"* ]]; then
    echo "ERROR: Backup base directory '$BACKUP_BASENAME/' not found in archive!"
    echo "First entry: $FIRST_ENTRY"
    exit 1
fi
echo "✓ Backup base directory present"

echo ""
echo "=== Verification Summary ==="
echo "Archive: $BACKUP_TAR"
echo "Size: $(numfmt --to=iec-i --suffix=B $FILE_SIZE 2>/dev/null || echo ${FILE_SIZE} bytes)"
echo "Files: $FILE_COUNT"
echo "Status: ✓ All integrity checks passed"
    """,
    dag=dag,
)

# Task 4: Rotate old backups
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
create_backup >> compress_backup >> verify_backup >> rotate_backups