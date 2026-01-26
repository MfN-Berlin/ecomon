#!/bin/bash

# Simple export using COPY TO (CSV)
# Usage: ./export_minimal_data.sh <container_name> <db_user> <db_password> <site_prefix> [db_name] [start_date] [end_date]
#   start_date and end_date are optional, format: DD.MM.YYYY

set -euo pipefail

CONTAINER_NAME=${1:?container name required}
DB_USER=${2:?db user required}
DB_PASSWORD=${3:?db password required}
SITE_PREFIX=${4:?site prefix required}
DB_NAME=${5:-ecomon}
START_DATE=${6:-}
END_DATE=${7:-}
TS=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="export_${SITE_PREFIX}_${TS}"

# Convert DD.MM.YYYY to YYYY-MM-DD for PostgreSQL
convert_date() {
  local date_input=$1
  if [[ $date_input =~ ^([0-9]{2})\.([0-9]{2})\.([0-9]{4})$ ]]; then
    echo "${BASH_REMATCH[3]}-${BASH_REMATCH[2]}-${BASH_REMATCH[1]}"
  else
    echo "Invalid date format: $date_input (expected DD.MM.YYYY)" >&2
    exit 1
  fi
}

# Build date filter SQL
DATE_FILTER=""
if [[ -n "$START_DATE" ]] && [[ -n "$END_DATE" ]]; then
  START_DATE_SQL=$(convert_date "$START_DATE")
  END_DATE_SQL=$(convert_date "$END_DATE")
  DATE_FILTER="AND record_datetime >= '$START_DATE_SQL' AND record_datetime < '$END_DATE_SQL'::date + interval '1 day'"
  echo "Filtering records between $START_DATE and $END_DATE (inclusive)"
elif [[ -n "$START_DATE" ]]; then
  START_DATE_SQL=$(convert_date "$START_DATE")
  DATE_FILTER="AND record_datetime >= '$START_DATE_SQL'"
  echo "Filtering records from $START_DATE onwards"
elif [[ -n "$END_DATE" ]]; then
  END_DATE_SQL=$(convert_date "$END_DATE")
  DATE_FILTER="AND record_datetime < '$END_DATE_SQL'::date + interval '1 day'"
  echo "Filtering records up to $END_DATE (inclusive)"
fi

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
  SELECT * FROM records WHERE site_id = $SITE_ID $DATE_FILTER
) TO STDOUT WITH CSV HEADER" > "$OUTPUT_DIR/records.csv"

# model_inference_logs for those records
run_psql -c "\COPY (
  SELECT mil.*
  FROM model_inference_logs mil
  JOIN records r ON r.id = mil.record_id
  WHERE r.site_id = $SITE_ID $DATE_FILTER
) TO STDOUT WITH CSV HEADER" > "$OUTPUT_DIR/model_inference_logs.csv"

echo "✓ Export complete: $OUTPUT_DIR"

# Export statistics
echo ""
echo "Export statistics:"
run_psql -c "SELECT
  (SELECT COUNT(*) FROM records WHERE site_id = $SITE_ID $DATE_FILTER) AS records_count,
  (SELECT COUNT(*) FROM model_inference_logs mil JOIN records r ON mil.record_id = r.id WHERE r.site_id = $SITE_ID $DATE_FILTER) AS inference_logs_count,
  (SELECT COUNT(*) FROM site_directories WHERE site_id = $SITE_ID) AS directories_count,
  (SELECT COUNT(*) FROM site_reports WHERE site_id = $SITE_ID) AS reports_count;"