# Current State (as of 2026-09-11)

## IP Allocation Scheme (Legacy LAN — 10.10.10.0/24)
| Range | Purpose |
|---|---|
| `.1` | pfSense LAN gateway |
| `.2–.99` | Static IP reservations |
| `.100–.199` | DHCP dynamic pool |
| `.200–.254` | Reserved for future use |

> Legacy LAN still exists and carries the AP/WiFi and any untagged 
> devices. Being phased out as VLANs take over.

## VLANs
| VLAN | Name | Subnet | Gateway | Purpose |
|---|---|---|---|---|
| 10 | Management | `10.10.11.0/24` | `10.10.11.1` | Admin PC, future PiKVM |
| 20 | Servers | `10.10.20.0/24` | `10.10.20.1` | DC01, WIN11-01 |
| 30 | Clients | `10.10.30.0/24` | `10.10.30.1` | Mobile/WiFi devices |
| 40 | Security | `10.10.40.0/24` | `10.10.40.1` | Future Vaio, Kali |

DHCP range on every VLAN: `.100–.199`.

**VLAN status**: only **Servers (20)** has real devices on it (DC01 
confirmed working). Management, Clients, and Security exist in pfSense 
but are empty — see Known Pending Items.

![DC01 confirmed correct IP/gateway on Servers VLAN](attachments/Pasted%20image%2020260910164013.png)
![DC01 network details after VLAN migration](attachments/Pasted%20image%2020260910164024.png)

### Active Firewall Rules — LAN (legacy)
| # | Protocol | Source | Destination | Port | Action | Description |
|---|---|---|---|---|---|---|
| — | * | * | LAN Address | 80 | Pass | Anti-Lockout Rule (default) |
| 1 | any | LAN net | 10.10.10.21 | any | Pass | ⚠️ Stale — DC01 moved to `10.10.20.21` |
| 2 | TCP | 10.10.10.8 (main PC) | 192.168.0.20 | 8006 | Pass | Allow main PC → Proxmox WebUI |
| 3 | any | LAN net | !LAN net | any | Pass | Allow LAN → Internet |
| — | IPv4 | LAN subnets | any | any | Disabled | Legacy allow-any (kept as fallback) |
| — | IPv6 | LAN subnets | any | any | Disabled | Unused |

![Final LAN rules 1-3 configured](attachments/Pasted%20image%2020260910031956.png)

### Active Firewall Rules — per VLAN
| Interface | Source | Destination | Protocol | Action | Description |
|---|---|---|---|---|---|
| SERVERS | SERVERS subnet | any | any | Pass | Allow Servers → Internet |
| MANAGEMENT | MANAGEMENT subnet | any | any | Pass | Allow Management → Internet |
| CLIENTS | CLIENTS subnet | any | any | Pass | Allow Clients → Internet |
| SECURITY | SECURITY subnet | any | any | Pass | Allow Security → Internet |

No inter-VLAN rules exist yet — default-deny between segments until 
deliberate rules are added.

## NAT
Mode: **Automatic outbound NAT**, using dynamic "WAN address" reference.

![NAT outbound configuration](attachments/Pasted%20image%2020260910035318.png)

### Known Pending Items
- **DC01 rule (#1) is stale** — still points to `10.10.10.21`
- **Proxmox WebUI** sits outside pfSense entirely (`192.168.0.20:8006`, 
  on the ISP router's network)
- **AP/WiFi still on legacy flat LAN, untagged** — blocked on a managed 
  switch/AP with 802.1Q support
- **Main PC not yet migrated to Management VLAN**

---

# Change Log

### 2026-09-08/09 — Initial LAN lockdown
- Found default "allow any" rule active on LAN, no restrictions

![Default LAN rules before lockdown](attachments/Pasted%20image%2020260909151237.png)

- Added explicit rules: LAN→DC01, PC→Proxmox, LAN→Internet
- Disabled (not deleted) the default allow-any rule
- **Issue**: mobile lost internet — rule 3 was TCP-only, blocking DNS 
  (UDP). Fixed by setting protocol to `any`.

> ⚠️ **Broken link found**: original doc referenced an alias creation 
> screenshot (`Pasted image 20260909151624.png`) that doesn't exist in 
> the attachments folder. Either re-add it or remove the reference.

### 2026-09-10 — DHCP range conflict
- Attempted static mapping at `.50`, rejected — DHCP pool covered the 
  entire subnet

![DHCP static mapping rejected - IP within pool range](attachments/Pasted%20image%2020260910030141.png)

- Fixed: reduced DHCP pool to `.100–.199`

![DHCP pool range corrected](attachments/Pasted%20image%2020260910030105.png)

### 2026-09-10 — NAT reviewed
- Confirmed Automatic Outbound NAT, dynamic "WAN address" — correct for 
  a dynamic ISP-assigned public IP

### 2026-09-11 — VLAN segmentation implemented
- Enabled "VLAN aware" on Proxmox LAN bridge

![VLAN aware enabled on Proxmox bridge](attachments/Pasted%20image%2020260910154847.png)

- Tagged DC01/WIN11-01 with VLAN 20

![VM network device tagged VLAN 20](attachments/Pasted%20image%2020260910154951.png)

- Created 4 VLAN interfaces in pfSense, static IP per VLAN

![VLAN interface static IP assignment](attachments/Pasted%20image%2020260910160323.png)

- Enabled DHCP per VLAN

![DHCP ranges configured per VLAN](attachments/Pasted%20image%2020260910160913.png)

- Added baseline internet-access rule per VLAN
- **Issue (repeat)**: rules set to TCP only initially — same mistake as 
  the LAN lockdown. Fixed to `any`.

> ⚠️ **Broken links found**: original doc referenced "Rule 2" and 
> "Rule 3" firewall testing screenshots (`Pasted image 20260910032240.png` 
> and `20260910032308.png`) that don't exist in attachments. Same issue 
> as the alias screenshot above.

- Migrated DC01's DHCP static mapping: LAN → SERVERS, 
  `10.10.10.21` → `10.10.20.21`

![DHCP static mapping moved to Servers interface](attachments/Pasted%20image%2020260910162101.png)

### 2026-09-11 — Known blocker: physical VLAN segmentation incomplete
- AP connects to the legacy flat LAN, untagged — MGMT/CLIENTS/SECURITY 
  VLANs are configured but empty
- Blocked on: managed switch or AP with 802.1Q support

### **2026-09-16 — LAN gateway auto-selected as default, breaking WAN routing**

- **Symptom:** LAN clients got valid DHCP leases and could reach the pfSense GUI, but had no internet access. WAN gateway (WAN_DHCP) showed "pending" in Status > Gateways.
- **Root cause:** No IPv4 default gateway was explicitly pinned in System > Routing > Gateways. pfSense's automatic gateway-selection logic defaulted to LAN's gateway (LANGW) instead of WAN on every boot/reload, confirmed recurring across multiple reboots in system logs predating this session.
- **Contributing/secondary issue:** During interface reassignment via console (20:13), dhcpd briefly failed to bind to LAN ("no subnet declaration for vtnet1") — transient, self-resolved by the next filter reload once the interface's IP was consistently applied.
- **Fix:** System > Routing > Gateways > edit WAN_DHCP > check "Default Gateway" (IPv4) > save.
- **Verification:** Status > Gateways shows WAN_DHCP online (default); phone regained internet access.
- **Follow-up:** NTP fails to sync (config syntax error in ntpd startup, every boot) — clock reliability affects log timestamp accuracy; needs separate fix.

### **2026-09-16 — Aftermath of the issue**
- **DHCP Static Mapping**: Static mapping had an issue since it detected that the main laptop´s IP is already taken by a different device, so we had to change it from 10.10.10.8 to 10.10.10.23.
- **Firewall Proxmox Rule:** Since we have changed the IP address of the main laptop we had to modify the firewall rule source.