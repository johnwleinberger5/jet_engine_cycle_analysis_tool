#!/usr/bin/env bash
set -euo pipefail

IMAGE="engine-analysis"
OUTPUTS_DIR="$(pwd)/outputs"

mkdir -p "$OUTPUTS_DIR"

echo "Building Docker image: $IMAGE"
docker build -f docker/Dockerfile -t "$IMAGE" .

echo "Running trade study — outputs will appear in: $OUTPUTS_DIR"
docker run --rm -v "$OUTPUTS_DIR:/app/outputs" "$IMAGE"
