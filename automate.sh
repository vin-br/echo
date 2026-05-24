#!/usr/bin/env bash
# automate.sh — Run test coverage, start dev stack, and capture screenshots/GIFs.
#
# Usage:
#   ./automate.sh          # Full pipeline: coverage + automate
#   ./automate.sh --skip-coverage   # Skip coverage, run automate only
set -euo pipefail
cd "$(dirname "$0")"

SKIP_COVERAGE=false
for arg in "$@"; do
    case "$arg" in
        --skip-coverage) SKIP_COVERAGE=true ;;
    esac
done

echo "=== ECHO Automate Pipeline ==="

# Step 1: Generate test coverage report
if [ "$SKIP_COVERAGE" = false ]; then
    echo ""
    echo "--- Step 1: Generating test coverage report ---"
    pushd backend > /dev/null
    uv run pytest --cov=app --cov-report=html tests/
    popd > /dev/null
    echo "Coverage report generated at backend/htmlcov/"
else
    echo ""
    echo "--- Step 1: Skipping coverage (--skip-coverage) ---"
fi

# Step 2: Start the dev stack (backend + frontend + nginx)
echo ""
echo "--- Step 2: Starting dev stack ---"
./docker-dev.sh up -d backend-dev frontend-dev nginx-dev

echo "Waiting for backend health check..."
timeout=120
elapsed=0
until curl -sf http://localhost:8000/healthz > /dev/null 2>&1; do
    sleep 2
    elapsed=$((elapsed + 2))
    if [ "$elapsed" -ge "$timeout" ]; then
        echo "Error: Backend did not become healthy within ${timeout}s"
        exit 1
    fi
done
echo "Backend is healthy."

echo "Waiting for frontend..."
sleep 5

# Step 3: Run the automate tool
echo ""
echo "--- Step 3: Running automate (screenshots + GIFs) ---"
./docker-dev.sh run --rm automate-dev all

echo ""
echo "=== Automate pipeline complete ==="
echo "Screenshots and GIFs saved to media/"
