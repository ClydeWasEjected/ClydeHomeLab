# pfSense Installation

Related: [[pfSense Design]] · [[pfSense Network Configuration]] · [[pfSense Configuration]]

VM build and initial OS install for pfSense. Superseded network details live in [[pfSense Configuration]] — this doc is history only.

## VM specs used
- 2 vCPU
- RAM: doc conflict — build notes say 32 GB, but the actual "Memory" field entered was 4096 MB and [[pfSense Design]]'s spec table says 4 GB. Treat **4 GB as correct** unless verified otherwise on the live VM (`qm config <vmid>`).
- Network devices: `net0` → `vmbr0` (WAN, VirtIO) → ISP router; `net1` → `vmbr1` (LAN, VirtIO) → managed switch

## What was done
- Created the VM and both network devices as above; created `vmbr1` on the host for the LAN side.
- Installed pfSense via the standard installer (default options throughout).
- Completed the first-boot setup wizard with defaults, changed the admin password.

## Verification
![pfSense assigned an IP and the web GUI became reachable post-install](attachments/Pasted%20image%2020260908155146.png)
![Final state — pfSense 2.9.0-RELEASE fully installed and configured, hostname pfSense.JnClyde.lan](attachments/Pasted%20image%2020260908155943.png)
