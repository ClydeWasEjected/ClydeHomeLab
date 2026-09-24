# Homepage Design

Related: [[Homepage]] · [[svc-01]] · [Homelab - Inventory](<../1 - Infrastructure/Homelab - Inventory.md>)

Services dashboard for the lab: one page listing every service with its link and an up/down status, usable from the laptop and the phone.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Tool | **Homepage** (gethomepage.dev) | Solves the actual problem (knowing what runs where) with almost no resources. Config is plain YAML, which is practice for later IaC work. |
| Rejected for now | Zabbix, Grafana | Different problem. Zabbix is monitoring and alerting (server + database + frontend, too heavy for the A8). Grafana only draws data another system collects. Both belong to Phase D.5 Monitoring, on the Ryzen node, where Zabbix plus Grafana becomes a portfolio piece. |
| Host | `svc-01` (CT 106 on the A8) | Always on. Separate from `claude-srv` so a broken Docker update cannot take down Claude sessions, and the reverse. Moves to the Ryzen node when it is racked. |
| Runtime | Docker Compose | The whole service is one file, rebuildable in seconds. Config lives on the host through a bind mount, so the container is disposable. |
| Status checks | `siteMonitor` for anything with a web UI, `ping` for hosts without one | `href` is opened by the viewer's browser. `siteMonitor`/`ping` run from the container. A card can be green and still have a link that does not work from the phone. |
| VM access | Links to the Proxmox noVNC console on `proxmox-lab` | One click to the console, "Start Now" if the VM is off. Pinned to the lab node so the dashboard never starts the A8 rollback copy of DC01 (USN rollback risk). |

## Security rules

- Homepage has **no authentication**. Anyone who can reach `10.10.10.30:3000` sees the whole map of the lab.
- **Never port-forward it.** Remote access only through Tailscale.
- **No control actions** (start VM, run command) from the dashboard. Control stays inside tools that authenticate (Proxmox, SSH, claude.ai). API tokens, when added for widgets, are **read-only**.
- No credentials in YAML files.

## Remote access (phone)

Tailscale. The dashboard itself is reachable on `svc-01` once it joins the tailnet or a subnet route exists. Links to `10.10.10.x` only work from the phone once a Tailscale **subnet router** advertises `10.10.10.0/24`. Pending, see [[Homepage]].
