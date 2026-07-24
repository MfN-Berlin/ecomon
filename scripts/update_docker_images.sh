#!/usr/bin/env bash
set -euo pipefail

# Updates the images to the latest build, by pulling them from the GitHub registry, as built by CI.
# Last used images are kept and tagged with 'backup'. Older images are not rotated automatically.
# This will affect the images of the ecomon_val instance, not the images of the ecomon_next instance (those images are tagged with 'next'),
# except for Model Zoo, which is always updated, and Models themselves, which are pulled by Model Zoo.

GITHUB_REPOSITORY_OWNER=mfn-berlin

# Images to update
IMAGES=(
  "ghcr.io/${GITHUB_REPOSITORY_OWNER}/ecomon-frontend:latest"
#  "ghcr.io/${GITHUB_REPOSITORY_OWNER}/ecomon-api:latest"
#  "ghcr.io/${GITHUB_REPOSITORY_OWNER}/ecomon-worker:latest"
  "ghcr.io/${GITHUB_REPOSITORY_OWNER}/akwamo-webservice-next-dashboard:latest"
#  "ghcr.io/mfn-berlin/birdid-model-zoo"
)

echo "Starting update for images:"
printf ' - %s\n' "${IMAGES[@]}"
echo

for IMAGE in "${IMAGES[@]}"; do
    echo "=== Processing $IMAGE ==="

    # Check if image exists locally
    if docker image inspect "$IMAGE" >/dev/null 2>&1; then
        BASE_NAME="${IMAGE%:*}"
        BACKUP_TAG="${BASE_NAME}:backup"

        echo "Tagging current image as: $BACKUP_TAG"
        docker tag "$IMAGE" "$BACKUP_TAG"
    else
        echo "Image not found locally – skipping backup."
    fi

    echo "Pulling latest: $IMAGE"
    docker pull "$IMAGE"

    echo
done

echo "✔ Update complete!"
