#!/bin/bash
set -euo pipefail

# Function to search for .env file in the current directory and upper directories
find_dotenv() {
  current_dir=$(pwd)
  while [[ "$current_dir" != "/" ]]; do
    if [[ -f "$current_dir/.env" ]]; then
      echo "$current_dir/.env"
      return 0
    fi
    current_dir=$(dirname "$current_dir")
  done
  return 1
}

# Load environment variables from .env file if found
dotenv_file=$(find_dotenv)
if [[ -n "$dotenv_file" ]]; then
  echo "Loading environment variables from $dotenv_file"
  set -o allexport
  source "$dotenv_file"
  set +o allexport
else
  echo "No .env file found in current or upper directories"
  exit 1
fi

# Set default endpoint if not provided
: "${HASURA_GRAPHQL_ENDPOINT:=http://localhost:8080}"

# Run Hasura commands with error handling
{
  hasura metadata apply --admin-secret "$HASURA_ADMIN_SECRET" --endpoint "$HASURA_GRAPHQL_ENDPOINT"
  hasura migrate apply --admin-secret "$HASURA_ADMIN_SECRET" --endpoint "$HASURA_GRAPHQL_ENDPOINT"
  hasura seeds apply --admin-secret "$HASURA_ADMIN_SECRET" --endpoint "$HASURA_GRAPHQL_ENDPOINT"
} || {
  echo "An error occurred while running Hasura commands."
  exit 1
}

echo "Hasura commands executed successfully."
