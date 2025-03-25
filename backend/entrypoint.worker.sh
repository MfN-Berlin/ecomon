#!/bin/bash
set -eo pipefail

# Read environment variables for worker configuration
# (if not set, the defaults are used)
DB_WORKER_CONCURRENCY=${DB_WORKER_CONCURRENCY:-2}
INF_WORKER_CONCURRENCY=${INF_WORKER_CONCURRENCY:-1}

pids=()

start_db_worker() {
  echo "Starting DB worker with concurrency ${DB_WORKER_CONCURRENCY}"
  poetry run celery -A backend.worker.app.app worker -E -Q db_worker_queue -c ${DB_WORKER_CONCURRENCY} --hostname=db_worker@%%h &
  pids+=($!)
}

start_inf_worker() {
  echo "Starting Inference worker with concurrency ${INF_WORKER_CONCURRENCY}"
  poetry run celery -A backend.worker.app.app worker -E -Q inference_queue -c ${INF_WORKER_CONCURRENCY} --hostname=inf_worker@%%h &
  pids+=($!)
}

# Start one DB worker
start_db_worker

# Start one Inference worker
start_inf_worker

# Define a cleanup function for graceful shutdown
cleanup() {
    echo "Cleaning up all worker processes..."
    kill "${pids[@]}"
}

trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait