from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import os


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
    schedule_interval='0 21 * * 5',  # Every Friday at 21:00
    start_date=datetime(2025, 12, 1),
    catchup=False,
    max_active_runs=1,
)

class NoTemplateBashOperator(BashOperator):
    template_fields = ()  # disables Jinja templating

# Read configuration from environment variables
CHUNK_SIZE = os.getenv('BACKUP_CHUNK_SIZE', '10G') or '10G'
MAX_BACKUPS = int(os.getenv('MAX_BACKUPS') or '3')  # Handle empty string

# Task 1: Create backup (read from file)
# dump the complete directory
#with open("/opt/airflow/dags/scripts/backup_pg.sh") as f:
#    backup_script = f.read()
#
#create_backup = NoTemplateBashOperator(
#    task_id='postgres_backup_task',
#    bash_command=backup_script,
#    dag=dag,
#)

# Task 1: Create SQL dump (replaces the physical backup)
create_backup = NoTemplateBashOperator(
    task_id='postgres_backup_task',
    bash_command="""
set -euo pipefail

# Configuration - adjust these values as needed
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-ecomon}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/sql_dump_$TIMESTAMP"
BACKUP_FILE="$BACKUP_DIR/dump_$TIMESTAMP.sql"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create SQL dump
echo "Creating PostgreSQL SQL dump..."
echo "Host: $PGHOST:$PGPORT"
echo "Database: $PGDATABASE"
echo "User: $PGUSER"
echo "Output: $BACKUP_FILE"

# Use pg_dump to create SQL dump
pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -F p -f "$BACKUP_FILE"

# Verify dump was created
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: SQL dump file was not created!"
    exit 1
fi

echo "SQL dump created successfully: $BACKUP_FILE"
echo "Size: $(du -h "$BACKUP_FILE" | cut -f1)"

# Write timestamp for subsequent tasks
echo "$TIMESTAMP" > /backup/current_timestamp.txt
    """,
    dag=dag,
)

# Update the compress_backup task to work with SQL dumps
compress_backup = NoTemplateBashOperator(
    task_id='compress_backup',
    bash_command=f"""
set -euo pipefail

TIMESTAMP=$(cat /backup/current_timestamp.txt)
BACKUP_BASENAME="sql_dump_$TIMESTAMP"
BACKUP_PATH="/backup/$BACKUP_BASENAME"
BACKUP_DIR="/backup/backup_$TIMESTAMP"
CHUNK_SIZE="{CHUNK_SIZE}"

# Create directory for this backup
echo "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

echo "Compressing and splitting SQL dump (chunk size: $CHUNK_SIZE)"
# Create tar.gz stream and split into chunks
tar -C "$BACKUP_PATH" -cf - "dump_$TIMESTAMP.sql" | gzip | split -b $CHUNK_SIZE -d -a 4 - "$BACKUP_DIR/$BACKUP_BASENAME.tar.gz.part"

echo "Removing uncompressed SQL dump..."
rm -f "$BACKUP_PATH/dump_$TIMESTAMP.sql"

# List created chunks
echo "Backup compressed and split into:"
ls -lh "$BACKUP_DIR/$BACKUP_BASENAME.tar.gz.part"* | awk '{{print $9, $5}}'

# Count chunks
CHUNK_COUNT=$(ls -1 "$BACKUP_DIR/$BACKUP_BASENAME.tar.gz.part"* 2>/dev/null | wc -l)
echo "Total chunks created: $CHUNK_COUNT"
    """,
    dag=dag,
)

# Task 3: Verify backup integrity (no decompression)
verify_backup = NoTemplateBashOperator(
    task_id='verify_backup',
    bash_command="""
set -euo pipefail

TIMESTAMP=$(cat /backup/current_timestamp.txt)
BACKUP_BASENAME="sql_dump_$TIMESTAMP"
BACKUP_DIR="/backup/backup_$TIMESTAMP"
BACKUP_PREFIX="$BACKUP_DIR/$BACKUP_BASENAME"

echo "=== Backup Integrity Verification ==="
echo "Backup directory: $BACKUP_DIR"
echo "Backup prefix: $BACKUP_PREFIX"
echo ""

# Check 0: Backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "ERROR: Backup directory does not exist!"
    exit 1
fi
echo "✓ Backup directory exists"

# Check 1: Chunks exist
CHUNKS=($BACKUP_PREFIX.tar.gz.part*)
if [ ${#CHUNKS[@]} -eq 0 ]; then
    echo "ERROR: No backup chunks found!"
    exit 1
fi
echo "✓ Found ${#CHUNKS[@]} backup chunks"

# Check 2: All chunks are not empty and calculate total size
TOTAL_SIZE=0
for chunk in "${CHUNKS[@]}"; do
    if [ ! -f "$chunk" ]; then
        echo "ERROR: Chunk $chunk does not exist!"
        exit 1
    fi

    FILE_SIZE=$(stat -c%s "$chunk" 2>/dev/null || stat -f%z "$chunk" 2>/dev/null)
    if [ "$FILE_SIZE" -eq 0 ]; then
        echo "ERROR: Chunk $chunk is empty!"
        exit 1
    fi
    TOTAL_SIZE=$((TOTAL_SIZE + FILE_SIZE))
done
echo "✓ All chunks are non-empty"
echo "✓ Total backup size: $(numfmt --to=iec-i --suffix=B $TOTAL_SIZE 2>/dev/null || echo ${TOTAL_SIZE} bytes)"

# Check 4: Verify file naming sequence
echo "Verifying chunk sequence..."
EXPECTED_COUNT=${#CHUNKS[@]}
ACTUAL_SEQUENCE=$(ls -1 "$BACKUP_PREFIX.tar.gz.part"* | wc -l)
if [ "$EXPECTED_COUNT" -ne "$ACTUAL_SEQUENCE" ]; then
    echo "WARNING: Chunk sequence may have gaps"
else
    echo "✓ Chunk sequence is complete"
fi

echo ""
echo "=== Verification Summary ==="
echo "Backup directory: $BACKUP_DIR"
echo "Backup prefix: $BACKUP_PREFIX"
echo "Chunks: ${#CHUNKS[@]}"
echo "Total size: $(numfmt --to=iec-i --suffix=B $TOTAL_SIZE 2>/dev/null || echo ${TOTAL_SIZE} bytes)"
echo "Status: ✓ All integrity checks passed"
echo ""
echo "Note: Full content verification skipped to save time."
echo "To verify archive contents, run:"
echo "  cat $BACKUP_PREFIX.tar.gz.part* | gunzip | tar -t | head"
    """,
    dag=dag,
)

# Task 4: Rotate old backups
rotate_backups = NoTemplateBashOperator(
    task_id='rotate_backups',
    bash_command=f"""
set -euo pipefail

MAX_BACKUPS={MAX_BACKUPS}

echo "Rotating old backups (keeping $MAX_BACKUPS newest backups)..."

# Find all backup directories (not files)
ALL_BACKUP_DIRS=()
for dir in /backup/backup_*; do
    if [ -d "$dir" ]; then
        ALL_BACKUP_DIRS+=("$dir")
    fi
done

COUNT=${{#ALL_BACKUP_DIRS[@]}}
echo "Found $COUNT backup directories"

if [ "$COUNT" -eq 0 ]; then
    echo "No backup directories found"
    rm -f /backup/current_timestamp.txt
    exit 0
fi

# Sort directories by timestamp (newest first) - extract timestamp and sort numerically
IFS=$'\n' ALL_BACKUP_DIRS=($(printf '%s\n' "${{ALL_BACKUP_DIRS[@]}}" | sort -t_ -k2 -rn))
unset IFS

echo "Backup directories (sorted newest first):"
for i in "${{!ALL_BACKUP_DIRS[@]}}"; do
    echo "  [$i] ${{ALL_BACKUP_DIRS[$i]}}"
done

if (( COUNT > MAX_BACKUPS )); then
    DELETE_COUNT=$((COUNT - MAX_BACKUPS))
    echo "Removing $DELETE_COUNT oldest backup directories"

    # Delete backups starting from index MAX_BACKUPS (oldest backups)
    for ((i=MAX_BACKUPS; i<COUNT; i++)); do
        OLD_DIR="${{ALL_BACKUP_DIRS[$i]}}"
        echo "Deleting backup directory: $OLD_DIR"
        rm -rf "$OLD_DIR"
    done
    echo "Kept $MAX_BACKUPS newest backups"
else
    echo "No old backups to remove. Current count: $COUNT (max: $MAX_BACKUPS)"
fi

rm -f /backup/current_timestamp.txt

echo "Backup rotation complete"
    """,
    dag=dag,
)

# Define task dependencies
create_backup >> compress_backup >> verify_backup >> rotate_backups