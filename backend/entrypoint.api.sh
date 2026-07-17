#!/bin/bash
cd "$(dirname "$0")" || exit 1
poetry run python3 -m uvicorn backend.api.app:app --host 0.0.0.0 --port 80