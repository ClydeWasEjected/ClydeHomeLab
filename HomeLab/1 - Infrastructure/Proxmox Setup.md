# Proxmox Setup

Related: [[Proxmox Administration]] · [Homelab - Inventory](<Homelab - Inventory.md>)

Base install followed [NetworkChuck's Proxmox guide](https://www.youtube.com/watch?v=_u8qTN3cCnQ). This doc keeps only what was actually done and what broke — see [[Proxmox Administration]] for current bridge/network state, it supersedes the network info below.

## Access
`https://192.168.0.20:8006/` — still current; Proxmox mgmt UI sits outside pfSense on the ISP router's network (open item, see Inventory).

## What was done
- **Storage:** removed unused `local-lvm` (`lvremove /dev/pve/data`), reclaimed the space into `local` (`lvresize -l +100%FREE /dev/pve/root`, `resize2fs /dev/mapper/pve-root`).
- **Network verification:** confirmed uplink active, pinged `8.8.8.8` and resolved DNS before proceeding.
- **VM network:** all VMs bridged through `vmbr0` initially (pre-pfSense, flat `192.168.0.0/24`). Superseded by the pfSense/VLAN build — see [[Proxmox Administration]] and [Homelab - Inventory](<Homelab - Inventory.md>) §2 for current bridges and subnets.

## Verification
![local storage reclaimed — 974.38 GB available after lvremove/lvresize/resize2fs](attachments/Pasted%20image%2020260531001406.png)
![connectivity confirmed — 8.8.8.8 and google.com both responding pre-VM-deployment](attachments/Pasted%20image%2020260531001712.png)

## Issues encountered

**KVM virtualization not available** — VM failed to start ("KVM virtualisation configured, but not available"). Cause: AMD SVM disabled in BIOS. Fix: enabled SVM, cold-booted, confirmed KVM module loaded.

**Invalid VM network bridge** — VM failed to start ("bridge is neither a linux nor an OVS bridge"). Cause: VM's network adapter was attached to the physical NIC instead of `vmbr0`. Fix: moved the adapter to `vmbr0`.
