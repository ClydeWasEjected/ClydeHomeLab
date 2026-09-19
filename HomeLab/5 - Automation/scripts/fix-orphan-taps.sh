#!/bin/bash
# Watchdog: reattaches orphaned tapXXXiY interfaces to their expected bridge.
# Deployed at /usr/local/bin/fix-orphan-taps.sh on proxmox-a8, run via
# fix-orphan-taps.service + fix-orphan-taps.timer (OnBootSec=10, OnUnitActiveSec=60).
# See: HomeLab/1 - Infrastructure/Proxmox Administration.md

log="/var/log/bridge-tap-watchdog.log"
for tap in $(ip -o link show | grep -oP 'tap[0-9]+i[0-9]+'); do
        vmid=$(echo "$tap" | grep -oP 'tap\K[0-9]+')
        netidx=$(echo "$tap" | grep -oP 'i\K[0-9]+')
        if ip link show "$tap" | grep -q "master"; then
                echo "$tap tiene master"
        else
                echo "$tap no tiene master"
                bridge_esperado=$(qm config "$vmid" | grep "net${netidx}:" | grep -oP 'bridge=\K[^,]+')
                echo "$bridge_esperado"
                date_now=$(date "+%Y-%m-%d %H:%M:%S")
                if ip link set "$tap" master "$bridge_esperado"; then
                        echo "bridge linked"
                        echo "$date_now - fixed $tap -> $bridge_esperado" >> "$log"
                else
                        echo "$date_now - failed to connect tap to bridge" >> "$log"
                fi
        fi
        echo ""
done
