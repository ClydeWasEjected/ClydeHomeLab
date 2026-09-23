# Active Directory Design

Related: [[AD Administration]] · [[DC01]] · [[WIN11-01]] · [Homelab - Inventory](<../1 - Infrastructure/Homelab - Inventory.md>)

## Objective
Deploy and simulate a basic enterprise Active Directory environment using Windows Server 2022 and Windows 11 clients for:

- Domain authentication
- DNS infrastructure
- Group Policy management
- Identity and access control testing

## Architecture

### Components
- **DC01** (Windows Server 2022) → Domain Controller + DNS
- **WIN11-01** (Windows 11 Enterprise) → Domain Client
- **Proxmox Host** → Virtualization platform

### Network placement

Both DC01 and WIN11-01 live on the **Servers VLAN (20)** — see [[pfSense Configuration]] for the VLAN plan and [Homelab - Inventory](<../1 - Infrastructure/Homelab - Inventory.md>) for current live IPs (don't duplicate exact IPs here; they drift).

Design rule: **DC01 is authoritative DNS for the domain and resolves itself** — every domain machine, DC01 included, must use DC01 as its DNS server. DC01 does not use the VLAN gateway as DNS.

## DNS Rules (Critical)

- All domain machines MUST use DC01 as DNS
- DC01 resolves:
    - Active Directory records
    - Internal domain (`ad.jnclydehl.local` — see Domain Configuration below)
- External resolution handled via DNS forwarders (see [[DC01]] for the forwarder list)

## Domain Configuration

- Domain: `ad.jnclydehl.local` — confirmed live via a direct DNS query against DC01 during the 2026-09-16 troubleshooting session (valid SOA returned). `DC01.md`'s build log says `jn.clydehl.local`, which is almost certainly a transcription error in that doc, not the real forest name — see [[DC01]].
- NetBIOS: likely `AD` (auto-derived from the domain above, matches the `AD\Administrator` whoami output in [[WIN11-01]]), not the `JNCLYDEHL` originally intended. Cheap to confirm with `Get-ADDomain` next time you're on DC01 — do that and remove this caveat.
- Forest Type: Single Domain Forest
- Functional Level: Windows Server 2022

## Why this structure

Departments chosen for the OU tree (IT / Security / Operations, see [[AD Administration]]) instead of a generic business template map to real permission narratives relevant to a security career path — each department gives a plausible reason for tiered access, service accounts, and delegation scenarios that later phases (privilege escalation, lateral movement, detection) can attack and defend against.

## Proxmox Virtualization Setup

**As of 2026-09-23, both VMs live on `proxmox-lab`, not the A8** — see [[Proxmox Lab Setup]] for the migration and current host details, and [Homelab - Inventory](<../1 - Infrastructure/Homelab - Inventory.md>) for current IPs (temporarily off VLAN 20, see there). Powered-off rollback copies of both remain on the A8. The specs below are what's actually running; don't treat this section as authoritative for network placement.

### Host Configuration
- Hypervisor: Proxmox VE, host `proxmox-lab` (was A8 before 2026-09-23)
- Storage: `local` (both hosts have `local-lvm` removed and reclaimed into `local` — see [[Proxmox Setup]] and [[Proxmox Lab Setup]])
- ISO storage: local

### VM Specifications

**DC01**
- Windows Server 2022
- 2 CPU
- 6GB RAM (bumped from 4GB 2026-09-23 for AD DS/DNS headroom — verify actually applied with `qm config 100 | grep ^memory`)
- 50GB Disk (`ide0` — not yet moved to VirtIO)

**WIN11-01**
- Windows 11 Enterprise
- 4 CPU (bumped from 2, while diagnosing lag — see [[Proxmox Lab Setup]])
- 6GB RAM (bumped from 4GB, same session)
- 60GB disk (`ide0` — not yet moved to VirtIO)
- CPU type: `x86-64-v2-AES` (was `cpu: host`, inherited from the AMD A8 build — caused visible lag once running on the lab node's Intel CPU; this was the actual fix, not the RAM/CPU bump)

![](attachments/Pasted%20image%2020260531005219.png)

