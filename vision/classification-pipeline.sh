#!/usr/bin/env bash
# classification-pipeline.sh — Launch the classification training CLI interactively.
#
# Usage:
#   ./classification-pipeline.sh                # Interactive mode (prompts for model, params)
#   ./classification-pipeline.sh --list-models  # Show available models
set -euo pipefail
exec uv run python -m vision.classification.cli --interactive "$@"
