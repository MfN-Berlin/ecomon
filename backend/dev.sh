#!/bin/bash

# Combined development starter for API + workers
set -x

# Start API server
poetry run uvicorn backend.api.app:app --host 0.0.0.0 --port 8000 --reload \
  & PID_API=$!

# Start DB worker with 2 concurrency
poetry run watchfiles --filter python \
  'poetry run celery -A backend.worker.app.app worker -E -Q db_worker_queue -c 2 --hostname=db_worker@%%h' \
  & PID_DB_WORKER=$!

# Start Inference worker with 1 concurrency
poetry run watchfiles --filter python \
  'poetry run celery -A backend.worker.app.app worker -E -Q inference_queue -c 1 --hostname=inf_worker@%%h' \
  & PID_INF_WORKER=$!

# Handle CTRL-C and cleanup
trap "kill $PID_API $PID_DB_WORKER $PID_INF_WORKER" SIGINT
wait $PID_API $PID_DB_WORKER $PID_INF_WORKER