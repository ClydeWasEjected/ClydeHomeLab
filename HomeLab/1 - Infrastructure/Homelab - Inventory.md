
> Single source of truth for hardware, IPs, and services. If a number in another note disagrees with this file, **this file wins** - update the other note. Related: [Homelab - Project Overview](Homelab%20-%20Project%20Overview.md)

## 1. Physical hardware

|Device|Role|Specs|Status|Why it's here|
|---|---|---|---|---|
|A8 (HP laptop)|Primary Proxmox node (bare metal)|AMD A8-9425, 24GB RAM|🟢 Active|Highest-RAM machine available; hosts everything infra-critical (pfSense, DC01, WIN11-01)|
|Gaming PC|Secondary Proxmox node (planned)|i5 10th-gen, 6C/12T, 16GB RAM|🟡 Blocked — no USB / no wired Ethernet at its location for install|Reserved for offensive-security VMs, kept off A8 on purpose|
|Ryzen 5 PRO 2400G mini PC|Docker / security services node (planned)|— (RAM expansion to 32GB planned)|⬜ Not yet racked|Offensive-security and service workloads once online|
|Vaio (Pentium 2020M)|Lightweight services node (planned)|4GB RAM|⬜ Not yet implemented|Migration exercise + Pi-hole/Home Assistant/Docker|
|~~Ryzen 3 / 8GB mini PC~~|—|—|⚫ Discarded|No longer part of the plan|

## 2. Network - VLANs (pfSense)

**⚠️ Verify before trusting:** `pfSense Configuration.md` (dated 2026-09-11) is the most recent source and is treated as authoritative below. `Network Design.md` and `pfSense Design.md` describe an earlier VLAN numbering (VLAN 20 = LAB-USERS, VLAN 30 = LAB-SERVERS) that **does not match** what's actually configured (VLAN 20 = Servers, VLAN 30 = Clients). Those two design docs need to be updated or explicitly marked "superseded."

| VLAN | Name       | Subnet          | Gateway      | Purpose                                             | Real devices on it today                           |
| ---- | ---------- | --------------- | ------------ | --------------------------------------------------- | -------------------------------------------------- |
| —    | Legacy LAN | `10.10.10.0/24` | `10.10.10.1` | Pre-VLAN flat network; AP/WiFi and untagged devices | Main PC (`10.10.10.8`), AP/WiFi - being phased out |
| 10   | Management | `10.10.11.0/24` | `10.10.11.1` | Admin PC, future PiKVM                              | Empty — Main PC not yet migrated here              |
| 20   | Servers    | `10.10.20.0/24` | `10.10.20.1` | DC01, WIN11-01                                      | **DC01, WIN11-01** - the only populated VLAN       |
| 30   | Clients    | `10.10.30.0/24` | `10.10.30.1` | Mobile/WiFi devices                                 | Empty                                              |
| 40   | Security   | `10.10.40.0/24` | `10.10.40.1` | Future Vaio, Kali                                   | Empty                                              |

DHCP range on every VLAN: `.100–.199`.

## 3. Devices - IP / DNS / domain status

**⚠️ Conflicting values found across notes - flagged per row.** Treat the "Current (best guess)" column as needing your confirmation, not as settled fact.

| Device            | Current (best guess)                                                      | Conflicting values found                                                                                                                                           | Source of conflict                                                                        |
| ----------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| Proxmox host (A8) | `192.168.0.20` — sits **outside pfSense**, on the ISP router's network    | `192.168.0.10` in `Homelab Overview.md`; `192.168.0.20` in `Proxmox Setup.md` and `pfSense Configuration.md`                                                       | Overview.md predates the pfSense migration and was never updated                          |
| DC01              | `10.10.20.21`, VLAN 20 (Servers)                                          | `192.168.0.21` in `DC01.md`; `10.10.10.21` in an old (now-stale) pfSense rule; `10.10.20.21` confirmed in `pfSense Configuration.md` and `Active Directory Lab.md` | `DC01.md` was never updated after the VLAN migration                                      |
| WIN11-01          | `10.10.20.22`, VLAN 20 (Servers), gateway `10.10.20.1`, DNS `10.10.20.21` | `192.168.0.22 (planned)` in `Proxmox Setup.md`                                                                                                                     | Proxmox Setup.md predates the actual WIN11-01 build — `WIN11-01.md` has the current value |
| Main PC           | `10.10.10.8` (legacy LAN)                                                 |                                                                                                                                                                    | Pending migration to Management VLAN (10)                                                 |
| Domain name       | Needs one confirmed form                                                  | `jnclydehl.local` (Overview/Design docs), `ad.jnclydehl.local` (WIN11-01 domain join), `jn.clydehl.local` (typo in `DC01.md`)                                      | Never standardized after DC01 promotion                                                   |
| NetBIOS           | `JNCLYDEHL`                                                               | consistent everywhere it appears                                                                                                                                   |                                                                                           |

## 4. Services running

|Service|Runs on|Purpose|
|---|---|---|
|pfSense|VM on A8 (Proxmox)|Router/firewall, DHCP, DNS forwarding, VLAN segmentation|
|Active Directory Domain Services + DNS|DC01 (VM on A8)|Domain authentication, name resolution for the domain|
|Tailscale|Installed on the A8 Proxmox host only|Secure remote management of Proxmox (and by extension all VMs/consoles) without exposing ports to the internet|

## 5. Known documentation debt (from this review)

- [ ] Reconcile domain name to one canonical value everywhere (`DC01.md` has a typo: `jn.clydehl.local`)
- [x] Update `DC01.md` network section — still shows the pre-VLAN IP (`192.168.0.21`)
- [ ] Remove/disable the stale pfSense rule pointing at `10.10.10.21` for DC01
- [x] Update or mark superseded: `Network Design.md` and `pfSense Design.md` (VLAN numbering doesn't match what's actually deployed)
- [x] Fill in the incomplete section in `WIN11-01.md` (placeholder line never completed)
- [ ] Empty index files with no content: `HomeLab.md`, `1 - Infrastructure.md`, `2 - Microsoft.md`, `3 - Remote Access.md`, `4 - pfSense.md` — either populate as folder landing pages or remove
- [ ] `HomeLab/Plan.md`, `Roles.md`, `Roles 2.md` are early brainstorming notes (mention hardware since discarded, e.g. Ryzen 3, and tools never adopted, e.g. Fortinet/Netgear firewalls) — archive them or mark clearly as superseded so they don't get read as current
- [ ] **Security note:** `Homelab Overview.md` and `DC01.md` contain plaintext passwords (and a personal Gmail). Worth moving these out of notes that might get shared/exported and into a password manager, even for a lab environment