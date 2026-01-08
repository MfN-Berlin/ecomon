#!/bin/bash

# Simple export using COPY TO (CSV)
# Usage: ./export_minimal_data.sh <container_name> <db_user> <db_password> <site_prefix> [db_name]

set -euo pipefail

CONTAINER_NAME=${1:?container name required}
DB_USER=${2:?db user required}
DB_PASSWORD=${3:?db password required}
SITE_PREFIX=${4:?site prefix required}
DB_NAME=${5:-ecomon}
TS=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="export_${SITE_PREFIX}_${TS}"

run_psql() {
  # Use docker exec with proper arg passing and env var for password
  docker exec -e PGPASSWORD="$DB_PASSWORD" "$CONTAINER_NAME" \
    psql -X -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" "$@"
}

mkdir -p "$OUTPUT_DIR"

echo "Exporting data for site prefix: $SITE_PREFIX"

# Get site_id
SITE_ID=$(run_psql -t -A -c "SELECT id FROM sites WHERE prefix = '$SITE_PREFIX';" | xargs)

if [[ -z "$SITE_ID" ]]; then
  echo "No site found with prefix '$SITE_PREFIX'"
  exit 1
fi

echo "Found site_id: $SITE_ID"

# Export minimal related rows to CSV (COPY handles escaping)
# locations used by the site
run_psql -c "\COPY (
  SELECT *
  FROM locations
  WHERE id IN (SELECT DISTINCT location_id FROM sites WHERE prefix = '$SITE_PREFIX')
) TO STDOUT WITH CSV HEADER" > "$OUTPUT_DIR/locations.csv"

# models referenced by this site's inference logs
run_psql -c "\COPY (
  SELECT DISTINCT m.*
  FROM models m
  JOIN model_inference_logs mil ON mil.model_id = m.id
  JOIN records r ON r.id = mil.record_id
  WHERE r.site_id = $SITE_ID
) TO STDOUT WITH CSV HEADER" > "$OUTPUT_DIR/models.csv"

# sites (by prefix)
run_psql -c "\COPY (
  SELECT * FROM sites WHERE prefix = '$SITE_PREFIX'
) TO STDOUT WITH CSV HEADER" > "$OUTPUT_DIR/sites.csv"

# site_directories
run_psql -c "\COPY (
  SELECT * FROM site_directories WHERE site_id = $SITE_ID
) TO STDOUT WITH CSV HEADER" > "$OUTPUT_DIR/site_directories.csv"

# site_reports
run_psql -c "\COPY (
  SELECT * FROM site_reports WHERE site_id = $SITE_ID
) TO STDOUT WITH CSV HEADER" > "$OUTPUT_DIR/site_reports.csv"

# records
run_psql -c "\COPY (
  SELECT * FROM records WHERE site_id = $SITE_ID
) TO STDOUT WITH CSV HEADER" > "$OUTPUT_DIR/records.csv"

# model_inference_logs for those records
run_psql -c "\COPY (
  SELECT mil.*
  FROM model_inference_logs mil
  JOIN records r ON r.id = mil.record_id
  WHERE r.site_id = $SITE_ID
) TO STDOUT WITH CSV HEADER" > "$OUTPUT_DIR/model_inference_logs.csv"

echo "✓ Export complete: $OUTPUT_DIR"

# Export statistics
echo ""
echo "Export statistics:"
run_psql -c "SELECT
  (SELECT COUNT(*) FROM records WHERE site_id = $SITE_ID) AS records_count,
  (SELECT COUNT(*) FROM model_inference_logs mil JOIN records r ON mil.record_id = r.id WHERE r.site_id = $SITE_ID) AS inference_logs_count,
  (SELECT COUNT(*) FROM site_directories WHERE site_id = $SITE_ID) AS directories_count,
  (SELECT COUNT(*) FROM site_reports WHERE site_id = $SITE_ID) AS reports_count;"