#!/bin/bash
# Forced command bound to the GitHub Actions deploy key via authorized_keys
# (restrict,command="..."). Ignores anything the SSH client actually asked
# for except "deploy <script> <unit>", where both must be on the allowlist
# below. Reads the new script body from stdin, syntax-checks it before
# installing, then restarts only the matching timer.
# See: HomeLab/1 - Infrastructure/Proxmox Administration.md
set -euo pipefail

ALLOWED_SCRIPTS=("fix-orphan-taps.sh" "fix-down-interfaces.sh")
ALLOWED_UNITS=("fix-orphan-taps" "fix-down-interfaces")

read -r cmd script unit <<< "${SSH_ORIGINAL_COMMAND:-}"

if [ "$cmd" != "deploy" ]; then
    echo "denied: only 'deploy <script> <unit>' is allowed" >&2
    exit 1
fi

script_ok=0
for s in "${ALLOWED_SCRIPTS[@]}"; do [ "$s" = "$script" ] && script_ok=1; done
unit_ok=0
for u in "${ALLOWED_UNITS[@]}"; do [ "$u" = "$unit" ] && unit_ok=1; done

if [ "$script_ok" -ne 1 ] || [ "$unit_ok" -ne 1 ]; then
    echo "denied: script/unit not on allowlist" >&2
    exit 1
fi

tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT
cat > "$tmpfile"

if ! bash -n "$tmpfile"; then
    echo "denied: uploaded script fails bash -n syntax check, not installing" >&2
    exit 1
fi

install -m 0755 "$tmpfile" "/usr/local/bin/$script"

systemctl daemon-reload
systemctl restart "${unit}.timer"
systemctl list-timers "${unit}.timer" --no-pager
echo "deployed $script -> ${unit}.timer"
