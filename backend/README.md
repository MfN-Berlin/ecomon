# Ecomon Monitoring Data Analysis Backend

All User requests go through the hasura graphql api and then call by hasura webhooks
All longer running tasks are executed by the celery worker and storing results in the database

## Project structure

- `src/backend/api` - FastAPI application
- `src/backend/worker` - Celery worker all tasks are defined here
- `src/backend/shared` - Shared code between api and worker
- `src/backend/scripts` - Scripts for generating models and dummy data, insert labeles from csv

## Development

### Scripts

- generate-models - generate pydantic models from database `poetry run generate-models`
- generate-dummy-data - generate dummy data for testing `poetry run generate-dummy-data`
