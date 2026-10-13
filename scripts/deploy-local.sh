#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required." >&2
  exit 1
fi

echo "Building the application image..."
docker compose build app
echo "Starting PostgreSQL and application services..."
docker compose up -d db app
echo "Waiting for the application readiness endpoint..."
for attempt in $(seq 1 30); do
  if curl --fail --silent http://localhost:8000/health/ready >/dev/null; then
    echo "Local deployment is ready: http://localhost:8000"
    exit 0
  fi
  sleep 2
done

echo "Deployment did not become ready. Recent logs:"
docker compose logs --tail=80 app db
exit 1
