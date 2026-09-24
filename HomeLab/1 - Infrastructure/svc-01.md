# svc-01

Related: [Homelab - Inventory](<Homelab - Inventory.md>) · [[Proxmox Administration]] · [[claude-srv]]

Docker host for lab services. First workload: the Homepage dashboard. Temporary home for containers until the Ryzen node is racked.

## Current State

| Item | Value |
|---|---|
| Proxmox host / ID | `proxmox-a8`, CT 106 |
| Type | Unprivileged LXC, `nesting=1,keyctl=1` (both needed for Docker in an unprivileged CT) |
| OS | Debian 13 (`debian-13-standard_13.6-1`) |
| Resources | 2 cores, 2048 MB RAM, 512 MB swap, 16 GB rootfs on `local` |
| Network | `net0` on `vmbr1`, Proxmox firewall flag on, **static** `10.10.10.30/24`, gw `10.10.10.1`, DNS `10.10.10.1` |
| Start on boot | Yes |
| Docker | Docker CE 29.8.1 + Compose v5.5.1, from Docker's official Debian repo (`/etc/apt/sources.list.d/docker.sources`) |
| Users | `root` (no password, `pct enter 106` from the A8), `adm-jnclyde` (sudo, docker) |
| Containers | `homepage` (see [[Homepage]]) |

## Change Log

### 2026-09-24: Built, replaces CT 104

- **Why:** CT 104 (`ubuntu`) was an undocumented test container found during the dashboard planning. Audit results:
  - **Privileged** (`unprivileged: 0`) with `lxc.apparmor.profile: unconfined`. Root in the container was root on the A8, the host that runs pfSense.
  - Ran Docker (official repo) with a `netbootxyz` PXE container (TFTP `69/udp`, web `3000/tcp` on all interfaces) plus 4 leftover `hello-world` containers.
  - Shell history showed AppArmor being disabled by hand to get Docker to start.
  - DHCP `10.10.10.125`, start at boot off, only user `root`.
- Backed up before destroying: `/var/lib/vz/dump/vzdump-lxc-104-2026_09_24-02_00_57.tar.zst` (2.1 GB, includes `/root/netboot` assets and config). Restorable with `pct restore`.
- Destroyed CT 104. Created CT 106 from the Debian 13 template, unprivileged, static IP outside the DHCP range (`.100`-`.199`).
- Installed Docker from the official repo.
- **Verification:** `hello-world` ran successfully with no AppArmor changes, then the image was removed. Internet and DNS reachable from the CT.
- Created admin account `adm-jnclyde` (groups `sudo`, `docker`) per the naming convention in [[AD Administration]]. Note: `docker` group membership is root-equivalent on this host.
- Deployed Homepage, see [[Homepage]].
- **Pending:** SSH access for `adm-jnclyde`, phone access via Tailscale.
