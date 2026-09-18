**Host:** A8 (proxmox-a8), see [[Proxmox Setup]]

**Watchdog: fix-orphan-taps**
- Script: `/usr/local/bin/fix-orphan-taps.sh`
- Systemd units: `/etc/systemd/system/fix-orphan-taps.service`, `/etc/systemd/system/fix-orphan-taps.timer`
- Timer: `OnBootSec=10`, `OnUnitActiveSec=60`
- Log: `/var/log/bridge-tap-watchdog.log`
- Function: detects `tapXXXiY` interfaces with no `master` (bridge) assigned and automatically reattaches them to the correct bridge, looking up the expected bridge via `qm config <vmid>` on the matching `netN` line
- Status: active, verified live (hot). Persistence across a host reboot: **pending verification**

**Host bridges:**
- `vmbr0`: WAN / external network (192.168.0.0/24, uplink `enx00e04c4d6938`)
- `vmbr1`: Lab internal LAN (10.10.10.0/24, uplink `nic0`)

## Change Log

### 2026-09-17/18: Incident, LAN went down after toggling a NIC firewall setting in Proxmox

**Root cause:** modifying the Firewall checkbox on a running VM's NIC (hot hotplug) caused the tap interface to be recreated without being reattached to its bridge.

**Symptom:** [[pfSense Configuration]] showed the LAN interface with the correct IP from inside the VM, but the corresponding host side tap (`tap102i1`, later reproduced with `tap103i1` during testing) had no `master` in `bridge link`. Traffic reached the tap and went nowhere from there: LAN clients got no DHCP lease, pfSense webConfigurator unreachable over LAN.

**Manual fix:**
```bash
ip link set <tap> master <bridge>
```

**Automated fix:** `fix-orphan-taps.sh`. Loops through every `tapXXXiY` interface on the host, checks whether it has a `master`, and if not, queries `qm config <vmid>` to find the expected bridge, reattaches it with `ip link set`, and logs timestamp, tap, and bridge.

**Automation:** systemd `.service` (oneshot) + `.timer` (60s) instead of cron, for `journalctl` integration.

**Verification:** tested end to end by forcing `ip link set tap103i1 nomaster`. The watchdog detected and reattached it automatically within the next timer run (≤60s), confirmed via `bridge link` and `journalctl -u fix-orphan-taps.service`.

**Pending:**
- Verify VM 103's net1 config persists correctly across a host reboot, not just when set live
- Confirm whether the hotplug bug is consistently reproducible or intermittent