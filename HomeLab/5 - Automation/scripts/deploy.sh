#!/bin/bash
# Deploy a watchdog script to proxmox-a8 via the restricted CI deploy key,
# and verify its timer picked it up. Same script used locally and by
# .github/workflows/deploy.yml, so local and CI deploys go through the
# identical path.
#
# Usage: ./deploy.sh <script-name> <unit-basename> [ssh-key-path]
# Example: ./deploy.sh fix-orphan-taps.sh fix-orphan-taps
set -euo pipefail

SCRIPT_NAME="$1"
UNIT="$2"
KEY="${3:-$HOME/.ssh/deploy-keys/homelab-ci-deploy}"
HOST="root@100.121.216.124"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_FILE="$SRC_DIR/$SCRIPT_NAME"

echo "==> local syntax check"
bash -n "$SRC_FILE"

echo "==> deploying $SCRIPT_NAME to $HOST (unit: ${UNIT}.timer)"
ssh -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new "$HOST" "deploy $SCRIPT_NAME $UNIT" < "$SRC_FILE"

echo "==> done"
