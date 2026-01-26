#!/bin/bash

# Import minimal dataset exported as CSVs (DB is always ecomon)
# Usage:
#   ./import_minimal_data.sh <container_name> <db_user> <db_password> <export_dir_in_container> [clean-mode]
# clean-mode: none | clean | clean-all

set -euo pipefail
trap 'echo "Import failed at: $BASH_COMMAND" >&2' ERR

CONTAINER_NAME=${1:?container name required}
DB_USER=${2:?db user required}
DB_PASSWORD=${3:?db password required}
EXPORT_DIR=${4:?export dir (inside container) required}
DB_NAME=ecomon
CLEAN_MODE=${5:-none} # none | clean | clean-all

run_psql() {
  docker exec -e PGPASSWORD="$DB_PASSWORD" "$CONTAINER_NAME" \
    psql -X -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" "$@"
}

echo "Importing into DB: $DB_NAME from: $EXPORT_DIR"
echo "Clean mode: $CLEAN_MODE"

# Check files exist in container
REQUIRED_FILES=(models.csv locations.csv sites.csv site_directories.csv site_reports.csv records.csv model_inference_logs.csv)
for f in "${REQUIRED_FILES[@]}"; do
  docker exec "$CONTAINER_NAME" test -f "$EXPORT_DIR/$f" || { echo "Missing $EXPORT_DIR/$f"; exit 1; }
done

# Optional cleanup (respect FK order)
if [[ "$CLEAN_MODE" == "clean" || "$CLEAN_MODE" == "clean-all" ]]; then
  run_psql -c "BEGIN"
  run_psql -c "DELETE FROM model_inference_logs"
  run_psql -c "DELETE FROM records"
  run_psql -c "DELETE FROM site_reports"
  run_psql -c "DELETE FROM site_directories"
  run_psql -c "DELETE FROM sites"
  run_psql -c "DELETE FROM locations"
  if [[ "$CLEAN_MODE" == "clean-all" ]]; then
    run_psql -c "DELETE FROM models"
  fi
  run_psql -c "COMMIT"

  # Reset sequences for cleared tables
  run_psql -c "SELECT setval('model_inference_logs_id_seq', 1, false)"
  run_psql -c "SELECT setval('records_id_seq',               1, false)"
  run_psql -c "SELECT setval('site_report_id_seq',           1, false)"
  run_psql -c "SELECT setval('site_directories_id_seq',      1, false)"
  run_psql -c "SELECT setval('sites_id_seq',                 1, false)"
  run_psql -c "SELECT setval('location_id_seq',              1, false)"
  if [[ "$CLEAN_MODE" == "clean-all" ]]; then
    run_psql -c "SELECT setval('models_id_seq', 1, false)"
  fi
fi

# Helper to copy and verify with per-table CSV options
copy_and_count() {
  local table="$1"
  local file="$2"
  local opts="$3"  # extra COPY options (do not repeat NULL)
  echo "Loading $table from $file..."
  run_psql -c "\copy $table FROM '$EXPORT_DIR/$file' WITH (FORMAT csv, HEADER true${opts})"
  run_psql -c "SELECT '$table' AS table, COUNT(*) AS rows FROM $table"
}

# Import in dependency-safe order
# models: CSV may have empty strings for integers -> use NULL '' and FORCE_NULL for nullable cols
# Table models has changed
# copy_and_count models           models.csv           ", NULL '',  FORCE_NULL (segment_duration, step_duration, updated_at, additional_docker_arguments, additional_model_arguments, remarks)"

# Other CSVs use empty strings for missing values
copy_and_count locations        locations.csv        ", NULL '', FORCE_NULL (remarks, updated_at)"

# sites explicit columns to handle empty updated_at
echo "Loading sites from sites.csv..."
run_psql -c "\copy sites FROM '$EXPORT_DIR/sites.csv' WITH (FORMAT csv, HEADER true, NULL '', FORCE_NULL (updated_at, remarks))"
run_psql -c "SELECT 'sites' AS table, COUNT(*) AS rows FROM sites"

copy_and_count site_directories site_directories.csv ", NULL ''"

# site_reports explicit columns (matching origin schema)
echo "Loading site_reports from site_reports.csv..."
run_psql -c "\copy site_reports (id, created_at, site_id, first_record_date, last_record_date, records_count, record_duration, corrupted_files, duration_histogram, daily_histogram, monthly_histogram, records_heatmap) FROM '$EXPORT_DIR/site_reports.csv' WITH (FORMAT csv, HEADER true, NULL 'null')"
run_psql -c "SELECT 'site_reports' AS table, COUNT(*) AS rows FROM site_reports"

# records explicit columns (no updated_at)
echo "Loading records from records.csv..."
run_psql -c "\copy records (id, site_id, filepath, filename, record_datetime, duration, channels, sample_rate, mime_type, created_at, errors) FROM '$EXPORT_DIR/records.csv' WITH (FORMAT csv, HEADER true, NULL 'null')"
run_psql -c "SELECT 'records' AS table, COUNT(*) AS rows FROM records"

# model_inference_logs explicit columns (no updated_at)
echo "Loading model_inference_logs from model_inference_logs.csv..."
run_psql -c "\copy model_inference_logs (model_id, record_id, analyzed, id) FROM '$EXPORT_DIR/model_inference_logs.csv' WITH (FORMAT csv, HEADER true, NULL 'null')"
run_psql -c "SELECT 'model_inference_logs' AS table, COUNT(*) AS rows FROM model_inference_logs"

# Fix sequences to max(id)
run_psql -c "SELECT setval('location_id_seq',             COALESCE((SELECT MAX(id) FROM locations),            1), true)"
run_psql -c "SELECT setval('sites_id_seq',                COALESCE((SELECT MAX(id) FROM sites),                1), true)"
run_psql -c "SELECT setval('site_directories_id_seq',     COALESCE((SELECT MAX(id) FROM site_directories),     1), true)"
run_psql -c "SELECT setval('site_report_id_seq',          COALESCE((SELECT MAX(id) FROM site_reports),         1), true)"
run_psql -c "SELECT setval('records_id_seq',              COALESCE((SELECT MAX(id) FROM records),              1), true)"
run_psql -c "SELECT setval('models_id_seq',               COALESCE((SELECT MAX(id) FROM models),               1), true)"
run_psql -c "SELECT setval('model_inference_logs_id_seq', COALESCE((SELECT MAX(id) FROM model_inference_logs), 1), true)"

echo "✓ Import complete."