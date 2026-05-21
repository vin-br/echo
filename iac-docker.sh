#!/usr/bin/env bash
# Provision ARC inside a Docker container using Ansible (no Vagrant/VirtualBox needed).
#
# Usage:
#   ./iac-docker.sh          # Start container, provision, verify
#   ./iac-docker.sh destroy  # Remove the container
set -euo pipefail

CONTAINER_NAME="arc-target"
IMAGE="ubuntu:24.04"
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

case "${1:-provision}" in
  destroy)
    echo "Removing container $CONTAINER_NAME..."
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
    echo "Done."
    ;;
  provision|"")
    # Start target container if not running
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
      echo "Starting target container ($IMAGE)..."
      docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
      docker run -d \
        --name "$CONTAINER_NAME" \
        -p 8082:8000 \
        -v "$PROJECT_ROOT:/app" \
        "$IMAGE" \
        sleep infinity
    else
      echo "Container $CONTAINER_NAME already running."
    fi

    # Run Ansible with Docker connection
    echo "Running Ansible provisioning..."
    ANSIBLE_CONFIG="$PROJECT_ROOT/iac/ansible.cfg" \
    ansible-playbook \
      -i "$PROJECT_ROOT/iac/playbooks/inventory.ini" \
      "$PROJECT_ROOT/iac/playbooks/main.yml"

    echo ""
    echo "Access the app at: http://localhost:8082"
    ;;
  *)
    echo "Usage: $0 [provision|destroy]"
    exit 1
    ;;
esac
