#!/bin/bash
# Watchdog: detects admin-down critical interfaces and brings them back up.
# Only touches WATCHED_IFACES plus any enx* USB NIC, never scans the whole host.
# Logs only state changes (down/recovered/missing), not every healthy run.
# Deployed at /usr/local/bin/fix-down-interfaces.sh on proxmox-a8, run via
# fix-down-interfaces.service + fix-down-interfaces.timer (OnBootSec=10, OnUnitActiveSec=60).
# See: HomeLab/1 - Infrastructure/Proxmox Administration.md

WATCHED_IFACES=("vmbr0" "vmbr1" "nic0")
LOG="/var/log/iface-down-watchdog.log"
STATE_DIR="/run/iface-down-watchdog"
mkdir -p "$STATE_DIR"

# USB NICs get names like enx<mac>; pick up whichever is plugged in
for path in /sys/class/net/enx*; do
    [[ -e "$path" ]] && WATCHED_IFACES+=("$(basename "$path")")
done

log() { echo "$(date '+%F %T') $*" >> "$LOG"; }

# Log only when the state differs from the previous run
set_state() {
    local iface=$1 new=$2 msg=$3
    local file="$STATE_DIR/$iface"
    [[ "$(cat "$file" 2>/dev/null)" == "$new" ]] && return
    echo "$new" > "$file"
    log "$iface $msg"
}

for iface in "${WATCHED_IFACES[@]}"; do
    if ! ip link show "$iface" &>/dev/null; then
        set_state "$iface" missing "not found on host"
        continue
    fi

    flags=$(ip -o link show "$iface" | sed -n 's/.*<\(.*\)>.*/\1/p')

    if [[ ",$flags," == *",UP,"* ]]; then
        set_state "$iface" up "up"
    elif ip link set "$iface" up; then
        log "$iface was admin-down, brought up"
        echo up > "$STATE_DIR/$iface"
    else
        set_state "$iface" failed "was admin-down, failed to bring up"
    fi
done
