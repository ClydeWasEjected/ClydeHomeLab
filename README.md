# 🏠 ad.jnclydehl.local — Cybersecurity Career Homelab

**A self-built enterprise network, run through a deliberate career-transition curriculum: understand the system, attack it, detect the attack, fix it.**

![Status](https://img.shields.io/badge/status-active--build-brightgreen)
![Phase](https://img.shields.io/badge/phase-A%2FB%2FC%20in%20progress-blue)
![Domain](https://img.shields.io/badge/domain-ad.jnclydehl.local-informational)
![Hypervisor](https://img.shields.io/badge/hypervisor-Proxmox%20VE-orange)
![Firewall](https://img.shields.io/badge/firewall-pfSense-00a99d)

---

## 👋 About this lab

I'm Clyde, an IT Support Tech (N1/N2) at Econocom, deployed on-site at Mango's Barcelona offices. The day job gives me real enterprise ticket, AD, M365, and hardware exposure. This repo is where I build the parts the job doesn't give me: a network I own end to end, that I can **build, break, monitor, and rebuild** on purpose.

The goal is a red team / SOC-analyst career transition. But this lab is deliberately not Kali-and-CTFs-first. The sequencing is intentional:

```
IT fundamentals → Sysadmin → Windows/AD → Microsoft Cloud → Networking/Security → Offensive Security
```

You can't attack, or defend, a system you don't understand. So infrastructure fundamentals come first, and offensive tooling stays out of scope until the foundation underneath it is solid.

## 🗺️ Current architecture

```
                         INTERNET
                             │
                          Router
                             │
                      ┌──────▼──────┐
                      │   pfSense   │  firewall / NAT / VLAN routing
                      └──────┬──────┘
                             │
                 ┌───────────┼────────────┬────────────┐
              VLAN 10      VLAN 20      VLAN 30       VLAN 40
            Management     Servers      Clients       Security
           (10.10.11.0/24)(10.10.20.0/24)(10.10.30.0/24)(10.10.40.0/24)
                             │
                    ┌────────┴────────┐
                    │  Proxmox (A8)   │  always-on primary node
                    ├─────────────────┤
                    │ DC01     .20.21 │  AD DS + DNS
                    │ WIN11-01 .20.22 │  domain-joined client
                    └─────────────────┘

        Remote management: Tailscale (Proxmox host, A8)
```

> Second Proxmox node (i5 gaming PC) is coming online as an on-demand box for offensive-security VMs, kept deliberately separate from the always-on A8, since infra-critical services (pfSense, DC01) never live on hardware that isn't always up.

## 🧰 Stack

| Layer | Tooling |
|---|---|
| Hypervisor | Proxmox VE |
| Firewall / Routing | pfSense |
| Identity | Windows Server: Active Directory Domain Services, DNS, GPOs |
| Remote access | Tailscale |
| Automation | Bash watchdogs deployed by a GitHub Actions CI/CD pipeline (ShellCheck, Tailscale, restricted SSH key). PowerShell in progress. |
| Planned | Entra ID, Intune, M365, Sysmon, centralized logging / SIEM |

## 🧭 Roadmap

| Phase | Focus | Status |
|---|---|---|
| A | pfSense: firewall rules, NAT, logging, allow/deny | 🟡 In progress |
| B | VLAN segmentation: Management / Servers / Clients / Security, inter-VLAN control | 🟡 Started (VLANs exist, mostly empty) |
| C | Enterprise AD: OUs, groups, service accounts, GPOs, delegation | 🟡 In progress |
| D | PowerShell / automation: scripted, rebuildable environments | ⬜ Pending |
| E | Microsoft Cloud: Entra ID, hybrid identity, M365, Intune, Autopilot, Conditional Access | ⬜ Pending |
| F | Security monitoring: Sysmon, event logging, SIEM (Wazuh), detection rules | ⬜ Pending |
| G | Offensive security lab: attacker node, recon, AD attacks, privesc, lateral movement | ⬜ Pending |
| H | Red team scenario + professional pentest report | ⬜ Pending |

**Cert path:** SC-900 → AZ-900 → SC-300 → AZ-104 → MD-102 → SC-200

## 📚 Documentation

Docs are split by service: a **Design** doc (architecture and rationale), a **build/implementation** doc (what was actually done), and an **Administration** doc (ongoing ops, dated change log) per component.

| Area | Docs |
|---|---|
| 🖥️ Infrastructure | [Project Overview](<HomeLab/1 - Infrastructure/Homelab - Project Overview.md>) · [Inventory](<HomeLab/1 - Infrastructure/Homelab - Inventory.md>) · [Proxmox Setup](<HomeLab/1 - Infrastructure/Proxmox Setup.md>) · [Proxmox Administration](<HomeLab/1 - Infrastructure/Proxmox Administration.md>) |
| 🔥 pfSense | [Design](<HomeLab/2 - pfSense/pfSense Design.md>) · [Installation](<HomeLab/2 - pfSense/pfSense Installation.md>) · [Network Configuration](<HomeLab/2 - pfSense/pfSense Network Configuration.md>) · [Configuration](<HomeLab/2 - pfSense/pfSense Configuration.md>) |
| 🌐 Remote Access | [Tailscale](<HomeLab/3 - Remote Access/Tailscale.md>) |
| 🪟 Microsoft / AD | [Active Directory Design](<HomeLab/4 - Microsoft/Active Directory Design.md>) · [AD Administration](<HomeLab/4 - Microsoft/AD Administration.md>) · [DC01](<HomeLab/4 - Microsoft/DC01.md>) · [WIN11-01](<HomeLab/4 - Microsoft/WIN11-01.md>) |
| ⚙️ Automation | [Design](<HomeLab/5 - Automation/Automation Design.md>) · [Administration](<HomeLab/5 - Automation/Automation Administration.md>) |
| 📋 Ops | [Incidents Log](<HomeLab/Incidents Log.md>) |

## 🚫 Deliberate non-goals (for now)

- No `allow any` firewall rules. The point of Phase A is understanding why a rule works, not making pings succeed.
- No jumping to Kali/exploitation before the infra it would attack actually exists.
- No infra-critical VM (pfSense, DC01) ever lands on hardware that isn't always-on.

---

<sub>Built and broken by Clyde. IT Support Tech to SOC/Red Team, in progress.</sub>
