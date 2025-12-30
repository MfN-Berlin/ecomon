#!/usr/bin/env bash
set -euo pipefail

part="$1"
log="./migrate_logs/${part//./_}.log"
start_time=$(date +%s)

echo "[$(date)] Checking $part..."

# Skip if already processed
already=$(docker exec "$CONTAINER" psql -U "$DBUSER" -d "$DBNAME" -Atc \
    "SELECT 1 FROM migration_progress WHERE partition_name='${part}'" || echo "")

if [[ "$already" == "1" ]]; then
    echo "✓ $part already completed. Skipping."
    exit 0
fi

# Check partition row count first
row_count=$(docker exec "$CONTAINER" psql -U "$DBUSER" -d "$DBNAME" -Atc \
    "SELECT count(*) FROM ${part}" 2>&1 | tee -a "$log")

echo "→ Processing $part ($row_count rows) (logs: $log)"

# Run migration with timeout and better error handling
if docker exec "$CONTAINER" psql -U "$DBUSER" -d "$DBNAME" \
    -v ON_ERROR_STOP=1 \
    <<EOSQL >> "$log" 2>&1
SET statement_timeout = '${STATEMENT_TIMEOUT}s';
SET work_mem = '512MB';
SET temp_buffers = '256MB';

BEGIN;

WITH best AS (
    SELECT record_id, label_id, model_id, MAX(confidence) AS max_confidence
    FROM ${part}
    GROUP BY record_id, label_id, model_id
),
dedup AS (
    SELECT DISTINCT ON (p.record_id, p.label_id, p.model_id) p.*
    FROM ${part} p
    JOIN best b
      ON p.record_id = b.record_id
     AND p.label_id  = b.label_id
     AND p.model_id  = b.model_id
     AND p.confidence = b.max_confidence
    ORDER BY p.record_id, p.label_id, p.model_id, p.id
)
INSERT INTO model_inference_results_max_confidence
(record_id, label_id, model_id, id, start_time, end_time, confidence)
SELECT record_id, label_id, model_id, id, start_time, end_time, confidence
FROM dedup
ON CONFLICT (record_id, label_id, model_id) DO UPDATE
SET
    id         = EXCLUDED.id,
    start_time = EXCLUDED.start_time,
    end_time   = EXCLUDED.end_time,
    confidence = EXCLUDED.confidence
WHERE EXCLUDED.confidence > model_inference_results_max_confidence.confidence;

INSERT INTO migration_progress(partition_name, row_count, duration_seconds)
VALUES ('${part}', ${row_count}, 0)
ON CONFLICT (partition_name) DO NOTHING;

COMMIT;
EOSQL
then
    end_time=$(date +%s)
    duration=$((end_time - start_time))

    # Update duration
    docker exec "$CONTAINER" psql -U "$DBUSER" -d "$DBNAME" -c \
        "UPDATE migration_progress SET duration_seconds = $duration WHERE partition_name = '${part}'" >> "$log" 2>&1

    echo "✓ Finished $part in ${duration}s"
else
    exit_code=$?
    echo "✗ FAILED $part (exit code: $exit_code) - check $log"
    echo "[$(date)] ERROR: Migration failed with exit code $exit_code" >> "$log"
    exit $exit_code
fi