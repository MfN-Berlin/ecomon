#!/bin/bash
set -euo pipefail

#############################################
# Validate environment variables
#############################################

: "${PG_USER:?PG_USER not set}"
: "${PG_PASSWORD:?PG_PASSWORD not set}"
: "${PG_HOST:?PG_HOST not set}"
: "${PG_PORT:?PG_PORT not set}"
: "${PG_DATABASE:?PG_DATABASE not set}"
: "${BACKUP_DIR:?BACKUP_DIR not set}"
: "${MAX_BACKUPS:?MAX_BACKUPS not set}"
: "${SPLIT_SIZE:?SPLIT_SIZE not set}"

#############################################
# Export vars for pg_basebackup
#############################################
export PGUSER="$PG_USER"
export PGPASSWORD="$PG_PASSWORD"
export PGHOST="$PG_HOST"
export PGPORT="$PG_PORT"
export PGDATABASE="$PG_DATABASE"

echo "Starting backup for database '$PGDATABASE' at $PGHOST:$PGPORT using user '$PGUSER'"

#############################################
# Prepare backup paths
#############################################
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_BASENAME="basebackup_$TIMESTAMP"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_BASENAME"
BACKUP_TAR="$BACKUP_PATH.tar.gz"
LOG_FILE="$BACKUP_DIR/backup_$TIMESTAMP.log"

mkdir -p "$BACKUP_DIR"

#############################################
# Run pg_basebackup
#############################################
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

#############################################
# Compress backup
#############################################
echo "Compressing backup..."
tar -C "$BACKUP_DIR" -czf "$BACKUP_TAR" "$BACKUP_BASENAME"

#############################################
# Split the backup file if configured
#############################################
echo "Splitting backup into chunks of $SPLIT_SIZE each..."
split -b "$SPLIT_SIZE" "$BACKUP_TAR" "$BACKUP_TAR.part_"

# Remove original directory + tar after splitting
rm -rf "$BACKUP_PATH" "$BACKUP_TAR"

#############################################
# Rotate old backups
#############################################
echo "Rotating old backups (keeping $MAX_BACKUPS)..."

# Find unique backup basenames
ALL_BACKUPS=($(ls -1 "$BACKUP_DIR"/basebackup_*.tar.gz.part_* 2>/dev/null \
    | awk -F'.tar.gz.part_' '{print $1}' | sort -u))

COUNT=${#ALL_BACKUPS[@]}

if (( COUNT > MAX_BACKUPS )); then
    DELETE_COUNT=$((COUNT - MAX_BACKUPS))
    echo "Removing $DELETE_COUNT oldest backups"

    for ((i=0; i<DELETE_COUNT; i++)); do
        OLD="${ALL_BACKUPS[$i]}"
        echo "Deleting: $OLD.*"
        rm -f "$OLD".tar.gz.part_*
    done
else
    echo "No old backups to remove."
fi

echo "Backup complete!"
