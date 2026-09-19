#!/bin/bash
# Watchdog: detects admin-down critical interfaces and brings them back up.
# Only touches interfaces in WATCHED_IFACES, never scans the whole host.
# Logs the state of every watched interface on every run.
# Deployed at /usr/local/bin/fix-down-interfaces.sh on proxmox-a8, run via
# fix-down-interfaces.service + fix-down-interfaces.timer (OnBootSec=10, OnUnitActiveSec=60).
# See: HomeLab/1 - Infrastructure/Proxmox Administration.md

WATCHED_IFACES=("vmbr0" "vmbr1" "enx00e04c4d6938" "nic0")
LOG="/var/log/iface-down-watchdog.log"

for iface in "${WATCHED_IFACES[@]}"; do
    if ! ip link show "$iface" &>/dev/null; then
        echo "$(date '+%F %T') $iface not found on host, skipping" >> "$LOG"
        continue
    fi

    flags=$(ip -o link show "$iface" | sed -n 's/.*<\(.*\)>.*/\1/p')

    if [[ ",$flags," == *",UP,"* ]]; then
        echo "$(date '+%F %T') $iface up, no action" >> "$LOG"
    else
        if ip link set "$iface" up; then
            echo "$(date '+%F %T') $iface was admin-down, brought up" >> "$LOG"
        else
            echo "$(date '+%F %T') $iface was admin-down, failed to bring up" >> "$LOG"
        fi
    fi
done
