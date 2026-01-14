#!/bin/bash
#
# Export model inference logs for a specific site to CSV.
#
# Usage:
#   ./export_model_inference_logs.sh --docker-container postgres --site-id 23
#   ./export_model_inference_logs.sh --docker-container my-postgres --user postgres --password mypass --site-id 23
#   ./export_model_inference_logs.sh --host localhost --site-id 23 --output logs.csv
#

set -euo pipefail

# Default values
DBNAME="ecomon"
USER="postgres"
PASSWORD="postgres"
HOST=""
DOCKER_CONTAINER=""
PORT="5432"
SITE_ID="23"
OUTPUT_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dbname)
            DBNAME="$2"
            shift 2
            ;;
        --user)
            USER="$2"
            shift 2
            ;;
        --password)
            PASSWORD="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --docker-container)
            DOCKER_CONTAINER="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --site-id)
            SITE_ID="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper function to run psql (defined AFTER arguments are parsed)
if [[ -n "$DOCKER_CONTAINER" ]]; then
    # Setup docker exec function
    run_query() {
        docker exec -e PGPASSWORD="$PASSWORD" "$DOCKER_CONTAINER" psql \
            -U "$USER" \
            -d "$DBNAME" \
            -w \
            "$@"
    }
else
    # Setup local psql function
    run_query() {
        PGPASSWORD="$PASSWORD" psql \
            -h "$HOST" \
            -U "$USER" \
            -d "$DBNAME" \
            -p "$PORT" \
            -w \
            "$@"
    }
fi

# Resolve host from docker container if specified
if [[ -n "$DOCKER_CONTAINER" ]]; then
    echo "Using Docker container '$DOCKER_CONTAINER' for database access" >&2
elif [[ -z "$HOST" ]]; then
    HOST="localhost"
fi

# Set default output file if not specified
if [[ -z "$OUTPUT_FILE" ]]; then
    OUTPUT_FILE="model_inference_logs_site_${SITE_ID}.csv"
fi

# Get min/max record_id for the site
echo "Site $SITE_ID: fetching record_id range..." >&2

BOUNDS=$(run_query -t -A -c "SELECT min(id) as min_id, max(id) as max_id FROM records WHERE site_id = $SITE_ID")

if [[ $? -ne 0 ]]; then
    echo "Error: Could not connect to database or query failed" >&2
    exit 1
fi

IFS='|' read -r MIN_ID MAX_ID <<< "$BOUNDS"

if [[ -z "$MIN_ID" ]] || [[ -z "$MAX_ID" ]]; then
    echo "Error: Could not determine record_id range for site_id=$SITE_ID" >&2
    echo "Query output was: '$BOUNDS'" >&2
    exit 1
fi

echo "  record_id range: $MIN_ID to $MAX_ID" >&2

# Export model_inference_logs data
echo "Fetching model_inference_logs data..." >&2

SQL="SELECT mil.id, mil.model_id, mil.record_id, mil.analyzed
FROM model_inference_logs mil
WHERE mil.record_id >= $MIN_ID
AND mil.record_id <= $MAX_ID
AND mil.record_id IN (SELECT id FROM records WHERE site_id = $SITE_ID)
ORDER BY mil.id;"

run_query --csv -c "$SQL" > "$OUTPUT_FILE"

if [[ $? -ne 0 ]]; then
    echo "Error: Query failed" >&2
    exit 1
fi

# Count rows
if [[ -s "$OUTPUT_FILE" ]]; then
    ROW_COUNT=$(wc -l < "$OUTPUT_FILE")
    ROW_COUNT=$((ROW_COUNT - 1))  # Subtract 1 for header row

    echo "" >&2
    echo "Export completed successfully:" >&2
    echo "  Site: $SITE_ID" >&2
    echo "  Total rows: $ROW_COUNT" >&2
    echo "  Output file: $OUTPUT_FILE" >&2
else
    echo "Error: No data retrieved from database" >&2
    exit 1
fi
