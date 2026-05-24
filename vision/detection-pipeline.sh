#!/usr/bin/env bash
# detection-pipeline.sh — Launch the detection training CLI interactively.
#
# Usage:
#   ./detection-pipeline.sh                    # Train with defaults
#   ./detection-pipeline.sh --epochs 50        # Override specific params
set -euo pipefail
exec uv run python -m vision.detection.cli "$@"
