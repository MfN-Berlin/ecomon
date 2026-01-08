#!/bin/bash
set -euo pipefail

# Export vars for pg_basebackup
export PGUSER="$PG_USER"
export PGPASSWORD="$PG_PASSWORD"
export PGHOST="$PG_HOST"
export PGPORT="$PG_PORT"
export PGDATABASE="$PG_DATABASE"

echo "Starting backup for database '$PGDATABASE' at $PGHOST:$PGPORT using user '$PGUSER'"

# Prepare backup paths
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_BASENAME="basebackup_$TIMESTAMP"
BACKUP_PATH="/backup/$BACKUP_BASENAME"
LOG_FILE="/backup/backup_$TIMESTAMP.log"

# Store timestamp for next tasks
echo "$TIMESTAMP" > /backup/current_timestamp.txt

echo "Running pg_basebackup..."
pg_basebackup \
    -U "$PGUSER" \
    -h "$PGHOST" \
    -p "$PGPORT" \
    -D "$BACKUP_PATH" \
    -F p \
    -X stream \
    -P \
    2>&1 | tee "$LOG_FILE"

echo "Backup directory created: $BACKUP_PATH"