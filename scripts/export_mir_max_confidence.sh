#!/bin/bash
#
# Export model inference results max confidence for a specific site to CSV.
#
# Usage:
#   ./export_mir_max_confidence.sh --docker-container postgres --site-id 23
#   ./export_mir_max_confidence.sh --docker-container my-postgres --user postgres --password mypass --site-id 23
#   ./export_mir_max_confidence.sh --host localhost --site-id 23 --output results.csv
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
    OUTPUT_FILE="model_inference_results_max_confidence_site_${SITE_ID}.csv"
fi

# Export model_inference_results_max_confidence data
echo "Site $SITE_ID: fetching model_inference_results_max_confidence data..." >&2

SQL="SELECT mirmc.id, mirmc.model_id, mirmc.record_id, mirmc.label_id, mirmc.start_time, mirmc.end_time, mirmc.confidence
FROM model_inference_results_max_confidence mirmc
INNER JOIN records r ON mirmc.record_id = r.id
WHERE r.site_id = $SITE_ID
ORDER BY mirmc.id;"

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
