#!/usr/bin/env bash
set -euo pipefail

IMAGE="engine-analysis"
OUTPUTS_DIR="$(pwd)/outputs"
NO_CACHE=""

for arg in "$@"; do
    case "$arg" in
        --no-cache) NO_CACHE="--no-cache" ;;
        *) echo "Unknown argument: $arg"; exit 1 ;;
    esac
done

mkdir -p "$OUTPUTS_DIR"

echo "Building Docker image: $IMAGE"
docker build $NO_CACHE -f docker/Dockerfile -t "$IMAGE" .

echo "Running trade study — outputs will appear in: $OUTPUTS_DIR"
docker run --rm -v "$OUTPUTS_DIR:/app/outputs" "$IMAGE"
