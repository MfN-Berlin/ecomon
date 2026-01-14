#!/bin/bash
#
# Export model inference results for models 0-7 and site_id=23 to CSV.
#
# Usage:
#   ./export_model_inference_results.sh --docker-container postgres
#   ./export_model_inference_results.sh --docker-container my-postgres --user postgres --password mypass
#   ./export_model_inference_results.sh --host localhost --site-id 23 --model-ids 0 1 2
#   ./export_model_inference_results.sh --docker-container postgres --output mir_results.csv
#
# To restore back into a database:
#   copy the output CSV into the database container, then import
#   docker cp mir_results.csv <container>:/tmp/mir_results.csv
#   psql -U <user> -d <dbname> -c "\COPY model_inference_results_pt_record(id, record_id, model_id, label_id, start_time, end_time, confidence) FROM '/tmp/mir_results.csv' WITH (FORMAT CSV, HEADER);"
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
MODEL_IDS=(0 1 2 3 4 5 6 7)
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
        --model-ids)
            shift
            MODEL_IDS=()
            while [[ $# -gt 0 ]] && [[ "$1" != --* ]]; do
                MODEL_IDS+=("$1")
                shift
            done
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
    OUTPUT_FILE="model_inference_results_site_${SITE_ID}.csv"
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

# Create temporary CSV file for accumulating results
TEMP_CSV=$(mktemp)
trap "rm -f $TEMP_CSV" EXIT

# Track if this is the first model (for header)
FIRST_MODEL=true

# Collect results from all models
for MODEL_ID in "${MODEL_IDS[@]}"; do
    echo "Fetching data for model_id=$MODEL_ID..." >&2

    SQL="SELECT *
FROM model_inference_results_pt_record mir
WHERE mir.model_id = $MODEL_ID
AND mir.record_id >= $MIN_ID
AND mir.record_id <= $MAX_ID
AND mir.record_id IN (SELECT id FROM records WHERE site_id = $SITE_ID)
ORDER BY mir.id;"

    # Query with header_only mode for first model, append mode for others
    if [[ "$FIRST_MODEL" == true ]]; then
        run_query --csv -c "$SQL" > "$TEMP_CSV"
        if [[ $? -ne 0 ]]; then
            echo "Error: Query failed for model_id=$MODEL_ID" >&2
            exit 1
        fi
        FIRST_MODEL=false
    else
        # For subsequent models, skip header and append
        run_query --csv -c "$SQL" | tail -n +2 >> "$TEMP_CSV"
        if [[ $? -ne 0 ]]; then
            echo "Error: Query failed for model_id=$MODEL_ID" >&2
            exit 1
        fi
    fi
done

# Unset password from environment
unset PGPASSWORD 2>/dev/null || true

# Count rows and copy to output
if [[ -s "$TEMP_CSV" ]]; then
    ROW_COUNT=$(wc -l < "$TEMP_CSV")
    ROW_COUNT=$((ROW_COUNT - 1))  # Subtract 1 for header row
    cp "$TEMP_CSV" "$OUTPUT_FILE"
else
    echo "Error: No data retrieved from database" >&2
    exit 1
fi

echo "" >&2
echo "Export completed successfully:" >&2
echo "  Models: ${MODEL_IDS[*]}" >&2
echo "  Site: $SITE_ID" >&2
echo "  Total rows: $ROW_COUNT" >&2
echo "  Output file: $OUTPUT_FILE" >&2
