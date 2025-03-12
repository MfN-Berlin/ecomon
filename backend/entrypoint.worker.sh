#!/bin/bash
poetry run celery -A backend.worker.app.app worker -E