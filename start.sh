#!/bin/bash

# Default to not building
BUILD_FLAG=""

# Check for --build or -b argument
if [[ "$1" == "--build" || "$1" == "-b" ]]; then
  BUILD_FLAG="--build"
  echo "Building Docker images..."
else
  echo "Using cached Docker images (use --build or -b to force rebuild)..."
fi

# Choose the Docker Compose file (default to GPU, but could add logic here to choose based on env var or arg)
# For now, assuming docker-compose.yml is the default as per original script
COMPOSE_FILE="docker-compose.yml"

# Execute docker compose up with the chosen file and build flag
cd "$(dirname "$0")"
docker compose -f $COMPOSE_FILE up $BUILD_FLAG