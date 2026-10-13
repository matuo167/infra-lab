#!/usr/bin/env bash
set -euo pipefail

base_url="${BASE_URL:-http://localhost:8000}"
curl --fail --silent "${base_url}/health/live" >/dev/null
curl --fail --silent "${base_url}/health/ready" >/dev/null
curl --fail --silent "${base_url}/api/tasks" >/dev/null
curl --fail --silent "${base_url}/metrics" | grep -q "http_requests_total"
echo "Smoke test passed for ${base_url}"
