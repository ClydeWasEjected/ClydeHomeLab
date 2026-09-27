#!/bin/bash
# Watchdog: reattaches orphaned guest ports to their expected bridge.
#   tapXXXiY   VM NIC        -> bridge from net<Y> (or fwbrXXXiY if firewall=1)
#   fwprXXXpY  firewall link -> bridge from net<Y> (LXC, or VM with firewall=1)
# A host networking reload (ifreload) detaches both kinds.
# Deployed at /usr/local/bin/fix-orphan-taps.sh on proxmox-a8, run via
# fix-orphan-taps.service + fix-orphan-taps.timer (OnBootSec=10, OnUnitActiveSec=60).
# See: HomeLab/1 - Infrastructure/Proxmox Administration.md

log="/var/log/bridge-tap-watchdog.log"
ports=$(ip -o link show | awk -F': ' '{print $2}' | cut -d@ -f1 | grep -E '^(tap[0-9]+i|fwpr[0-9]+p)[0-9]+$')
for port in $ports; do
        vmid=$(echo "$port" | grep -oP '^(tap|fwpr)\K[0-9]+')
        netidx=$(echo "$port" | grep -oP '[ip]\K[0-9]+$')
        if ip link show "$port" | grep -q "master"; then
                echo "$port tiene master"
                continue
        fi
        echo "$port no tiene master"
        # LXC config lives in /etc/pve/lxc, VM config in /etc/pve/qemu-server
        if [ -e "/etc/pve/lxc/${vmid}.conf" ]; then
                netconf=$(pct config "$vmid" | grep "^net${netidx}:")
        else
                netconf=$(qm config "$vmid" | grep "^net${netidx}:")
        fi
        bridge_esperado=$(echo "$netconf" | grep -oP 'bridge=\K[^,]+')
        # A firewalled VM's tap belongs on its fwbr, not on the vmbr
        if [[ "$port" == tap* ]] && echo "$netconf" | grep -q 'firewall=1'; then
                bridge_esperado="fwbr${vmid}i${netidx}"
        fi
        echo "$bridge_esperado"
        date_now=$(date "+%Y-%m-%d %H:%M:%S")
        if [ -n "$bridge_esperado" ] && ip link set "$port" master "$bridge_esperado"; then
                echo "bridge linked"
                echo "$date_now - fixed $port -> $bridge_esperado" >> "$log"
        else
                echo "$date_now - failed to connect $port to bridge '$bridge_esperado'" >> "$log"
        fi
        echo ""
done
