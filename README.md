# 🏠 ad.jnclydehl.local: Cybersecurity Career Homelab

**A self-built enterprise network, run through a deliberate career-transition curriculum: understand the system, attack it, detect the attack, fix it.**

![Status](https://img.shields.io/badge/status-active--build-brightgreen)
![Phase](https://img.shields.io/badge/phase-A%2FB%2FC%20in%20progress-blue)
![Domain](https://img.shields.io/badge/domain-ad.jnclydehl.local-informational)
![Hypervisor](https://img.shields.io/badge/hypervisor-Proxmox%20VE-orange)
![Firewall](https://img.shields.io/badge/firewall-pfSense-00a99d)

---

## 👋 About this lab

I'm Clyde, an IT support technician (N1/N2). My job gives me real enterprise exposure: tickets, Active Directory, M365 and hardware. This repo is where I build what the job doesn't give me: a network I own end to end, that I can **build, break, monitor, and rebuild** on purpose.

The goal is a SOC / red team career. This lab is deliberately not Kali-and-CTFs-first. The order is intentional:

```
IT fundamentals → Sysadmin → Windows/AD → Microsoft Cloud → Networking/Security → Offensive Security
```

You can't attack, or defend, a system you don't understand. So infrastructure fundamentals come first, and offensive tooling stays out of scope until the foundation underneath it is solid.

## 🗺️ Current architecture

```mermaid
flowchart TB
    net(("Internet")) --> isp["ISP router · 192.168.0.0/24"]
    isp --> pf

    subgraph a8["proxmox-a8 · always on"]
        pf["pfSense<br/>firewall · NAT · DHCP · VLANs"]
        cs["claude-srv<br/>ops container"]
        s1["svc-01<br/>Docker: dashboards"]
    end

    pf --> lan["LAN 10.10.10.0/24"]
    pf -. "defined, trunk pending" .-> vl["VLAN 10 Mgmt · 20 Servers<br/>30 Clients · 40 Security"]

    subgraph lab["proxmox-lab · second node"]
        dc["DC01<br/>AD DS + DNS"]
        w11["WIN11-01<br/>domain client"]
    end

    lan --> lab
    lan --> cs
    lan --> s1
    ts{{"Tailscale"}} -. "remote admin, no open ports" .-> a8
```

- Domain `ad.jnclydehl.local` on Windows Server 2022, one Windows 11 client.
- Two standalone Proxmox nodes (not clustered, on purpose: no quorum risk for the node running the firewall).
- DC01 and WIN11-01 sit on the flat LAN until a managed switch trunks VLAN 20 to the second node. Full detail in the [Inventory](<HomeLab/1 - Infrastructure/Homelab - Inventory.md>).

## 🧰 Stack

| Layer | Tooling |
|---|---|
| Hypervisor | Proxmox VE (2 nodes), LXC + KVM |
| Firewall / Routing | pfSense: explicit allow rules, default deny, per-VLAN DHCP |
| Identity | Windows Server 2022: AD DS, DNS, OUs, security groups (GPOs next) |
| Remote access | Tailscale (no router port forwards) |
| Automation | Bash watchdogs shipped by GitHub Actions: ShellCheck, ephemeral Tailscale node, forced-command SSH key. PowerShell next. |
| Services | Docker on an unprivileged LXC, self-hosted dashboards (Homepage + nginx), Syncthing |
| Planned | Entra ID, Intune, M365, Sysmon, Wazuh SIEM |

## 🔧 Problems solved so far

Real issues from building this, each with symptom, root cause, fix and verification in the docs:

| Problem | Root cause | Where |
|---|---|---|
| LAN had DHCP but no internet after a reboot | pfSense auto-picked the LAN gateway as default, WAN never pinned | [Incidents Log](<HomeLab/Incidents Log.md>) |
| Phones lost internet after the LAN lockdown | Allow rule was TCP only, so DNS (UDP) was dropped | [pfSense Configuration](<HomeLab/2 - pfSense/pfSense Configuration.md>) |
| pfSense admin password crossed the LAN in clear text | WebGUI served over HTTP; switched to HTTPS | [pfSense Configuration](<HomeLab/2 - pfSense/pfSense Configuration.md>) |
| VLAN 20 broke when VMs moved to a second host | Tagging only ever happened inside one Proxmox bridge; no physical 802.1Q path | [Proxmox Lab Setup](<HomeLab/1 - Infrastructure/Proxmox Lab Setup.md>) |
| Windows VM laggy after migration | `cpu: host` pinned to AMD, new node is Intel | [Proxmox Lab Setup](<HomeLab/1 - Infrastructure/Proxmox Lab Setup.md>) |
| DC clock 9 hours ahead | Wrong time zone, time set by hand, no NTP source (breaks Kerberos) | [DC01](<HomeLab/4 - Microsoft/Active Directory/DC01.md>) |
| Container escape risk | Privileged LXC with unconfined AppArmor, rebuilt unprivileged | [svc-01](<HomeLab/6 - Services/svc-01.md>) |
| CI needed SSH into the hypervisor | Deploy key locked to one allowlisted command | [Automation Design](<HomeLab/5 - Automation/Automation Design.md>) |

## 🧭 Roadmap

| Phase | Focus | Status |
|---|---|---|
| A | pfSense: firewall rules, NAT, logging, allow/deny | 🟡 In progress |
| B | VLAN segmentation: Management / Servers / Clients / Security, inter-VLAN control | 🟡 Started (VLANs exist, switch trunk pending) |
| C | Enterprise AD: OUs, groups, service accounts, GPOs, Windows LAPS, delegation | 🟡 In progress (C1 structure done, GPOs next) |
| D | PowerShell / automation: scripted, rebuildable environments | 🟡 Started (CI/CD for Bash watchdogs) |
| E | Microsoft Cloud: Entra ID, hybrid identity, M365, Intune, Autopilot, Conditional Access | ⬜ Pending |
| F | Security monitoring: Sysmon, event logging, SIEM (Wazuh), detection rules | ⬜ Pending |
| G | Offensive security lab: attacker node, recon, AD attacks, privesc, lateral movement | ⬜ Pending |
| H | Red team scenario + professional pentest report | ⬜ Pending |

**Cert path:** SC-900 → AZ-900 → SC-300 → AZ-104 → MD-102 → SC-200

## 📚 Documentation

**Start here:** [Project Overview](<HomeLab/1 - Infrastructure/Homelab - Project Overview.md>) for the big picture, [Inventory](<HomeLab/1 - Infrastructure/Homelab - Inventory.md>) for hardware, IPs and services (it wins any disagreement).

Docs are split by component, one folder per domain under `HomeLab/`:

- **Design**: architecture and rationale, not a diary.
- **Build** (named after the service or host): what was actually done, current state plus dated change log.
- **Administration**: ongoing procedures.

### 1 - Infrastructure
| Doc | What it covers |
|---|---|
| [Project Overview](<HomeLab/1 - Infrastructure/Homelab - Project Overview.md>) | Goals, roadmap, how the lab fits together |
| [Inventory](<HomeLab/1 - Infrastructure/Homelab - Inventory.md>) | Hardware, IPs, VMs and services (single source of truth) |
| [Proxmox Setup](<HomeLab/1 - Infrastructure/Proxmox Setup.md>) | Base install of the A8 node |
| [Proxmox Administration](<HomeLab/1 - Infrastructure/Proxmox Administration.md>) | Current bridges, network and ops on A8 |
| [Proxmox Lab Setup](<HomeLab/1 - Infrastructure/Proxmox Lab Setup.md>) | Second node `proxmox-lab`, VM migration |

### 2 - pfSense
| Doc | What it covers |
|---|---|
| [Design](<HomeLab/2 - pfSense/pfSense Design.md>) | Firewall architecture and rule philosophy |
| [Installation](<HomeLab/2 - pfSense/pfSense Installation.md>) | VM build and first boot |
| [Network Configuration](<HomeLab/2 - pfSense/pfSense Network Configuration.md>) | Interfaces, VLANs, DHCP |
| [Configuration](<HomeLab/2 - pfSense/pfSense Configuration.md>) | Rules, NAT, logging, hardening, change log |

### 3 - Remote Access
| Doc | What it covers |
|---|---|
| [Tailscale](<HomeLab/3 - Remote Access/Tailscale.md>) | Remote admin with no open ports |

### 4 - Microsoft

**Active Directory** (on-prem, phase C)

| Doc | What it covers |
|---|---|
| [Active Directory Design](<HomeLab/4 - Microsoft/Active Directory/Active Directory Design.md>) | Domain, OU and group model |
| [AD Administration](<HomeLab/4 - Microsoft/Active Directory/AD Administration.md>) | OUs, users, groups, GPOs, baselines (C1, C4) |
| [DC01](<HomeLab/4 - Microsoft/Active Directory/DC01.md>) | Domain controller build |
| [WIN11-01](<HomeLab/4 - Microsoft/Active Directory/WIN11-01.md>) | Domain-joined client build |
| [Remote Desktop](<HomeLab/4 - Microsoft/Active Directory/Remote Desktop.md>) | RDP into WIN11-01 (module C4+) |

**Entra and SSO** (cloud identity, phase E)

| Doc | What it covers |
|---|---|
| [Entra ID](<HomeLab/4 - Microsoft/Entra and SSO/Entra ID.md>) | Cloud identity, RBAC, Conditional Access, MFA (E1) |
| [Single Sign-On Design](<HomeLab/4 - Microsoft/Entra and SSO/Single Sign-On Design.md>) · [Single Sign-On](<HomeLab/4 - Microsoft/Entra and SSO/Single Sign-On.md>) | SSO design and implementation (E2) |

Windows LAPS (module C4b) has no vault doc yet; it exists only as a Hermes playbook.

### 5 - Automation
| Doc | What it covers |
|---|---|
| [Design](<HomeLab/5 - Automation/Automation Design.md>) | CI/CD and watchdog architecture |
| [Administration](<HomeLab/5 - Automation/Automation Administration.md>) | Running and changing the pipeline |
| [Job Pipeline Design](<HomeLab/5 - Automation/Job Pipeline Design.md>) | Semi-automatic job search (planning only) |
| `scripts/` | Watchdog and deploy scripts shipped by CI |

### 6 - Services
| Doc | What it covers |
|---|---|
| [Claude Server Design](<HomeLab/6 - Services/Claude Server Design.md>) · [claude-srv](<HomeLab/6 - Services/claude-srv.md>) | Always-on Claude Code LXC |
| [svc-01](<HomeLab/6 - Services/svc-01.md>) | Docker host for dashboards |
| [Homepage Design](<HomeLab/6 - Services/Homepage Design.md>) · [Homepage](<HomeLab/6 - Services/Homepage.md>) | Landing dashboard |
| [Hermes Design](<HomeLab/6 - Services/Hermes Design.md>) · [Hermes](<HomeLab/6 - Services/Hermes.md>) | Morning/evening email briefings |
| [Hermes Dashboard Design](<HomeLab/6 - Services/Hermes Dashboard Design.md>) · [Hermes Dashboard](<HomeLab/6 - Services/Hermes Dashboard.md>) | Dashboard and phase playbooks (academy) |
| [mock-apps](<HomeLab/6 - Services/mock-apps/README.md>) | Okta and Slack mock OAuth apps for red-team testing |

### 7 - AI Butler (side project)
| Doc | What it covers |
|---|---|
| [Design](<HomeLab/7 - AI Butler/AI Butler Design.md>) | Voice assistant plus Home Assistant, planning only |

### Cross-cutting (`HomeLab/` root)
| Doc | What it covers |
|---|---|
| [Incidents Log](<HomeLab/Incidents Log.md>) | Dated incidents: symptom, cause, fix |
| [Security Process](<HomeLab/Security Process.md>) | Audit cadence and rules (draft) |
| [Incident Response](<HomeLab/Incident Response.md>) | IR plan (draft v0, to redo as a tabletop) |

## 🚫 Deliberate non-goals (for now)

- No `allow any` firewall rules. The point of Phase A is understanding why a rule works, not making pings succeed.
- No jumping to Kali/exploitation before the infra it would attack actually exists.
- No infra-critical VM (pfSense, the service containers) ever lands on hardware that isn't always-on. The AD lab (DC01, WIN11-01) is a lab: it runs on the on-demand node.

---

<sub>Built and broken by Clyde. IT Support Tech to SOC/Red Team, in progress.</sub>
