#!/bin/bash
POSTGRES_HOST=localhost uvicorn app:app --reload --port 8888 --host 0.0.0.0
