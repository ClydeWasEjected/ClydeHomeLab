# Homepage

Related: [[Homepage Design]] · [[svc-01]] · [[pfSense Configuration]]

## Current State

| Item | Value |
|---|---|
| URL | `http://10.10.10.30:3000` |
| Host | `svc-01` (CT 106), user `adm-jnclyde` |
| Location | `~/homepage/` (`docker-compose.yml` + `config/`) |
| Image | `ghcr.io/gethomepage/homepage:latest` |
| Config | `~/homepage/config/*.yaml`, re-read on page load (no restart needed). Only `services.yaml` customised. |

### `docker-compose.yml`

```yaml
services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    ports:
      - "3000:3000"            # HOST:CONTAINER
    volumes:
      - ./config:/app/config   # HOST:CONTAINER
    environment:
      HOMEPAGE_ALLOWED_HOSTS: 10.10.10.30:3000
    restart: unless-stopped
```

### Services on the dashboard

| Group | Service | Link | Status check |
|---|---|---|---|
| Hypervisors | Proxmox-A8 | `https://192.168.0.20:8006` | siteMonitor |
| Hypervisors | Proxmox-lab | `https://10.10.10.2:8006` | siteMonitor |
| Microsoft Vms | DC01 | noVNC console, `proxmox-lab`, VM 100 | ping `10.10.10.21` |
| Microsoft Vms | WIN11-01 | noVNC console, `proxmox-lab`, VM 101 | ping `10.10.10.22` |
| Network | pfSense | `https://10.10.10.1` | siteMonitor |
| Servers | claude-srv | none | ping `10.10.10.124` |
| Servers | svc-01 | none | ping `10.10.10.30` |

Console link format: `https://<node-ip>:8006/?console=kvm&novnc=1&vmid=<id>&vmname=<name>&node=<node>`

### Operations (from `~/homepage`)

| Task | Command |
|---|---|
| Apply a change to `docker-compose.yml` | `docker compose up -d` |
| Apply a change to `config/*.yaml` | Save and refresh the browser |
| Logs (first stop when something breaks) | `docker compose logs -f homepage` |
| Update | `docker compose pull && docker compose up -d` |
| Stop and remove (config kept) | `docker compose down` |

## Change Log

### 2026-09-24: Built

- Wrote `docker-compose.yml` and brought it up on `svc-01`. First start generated the default config files.
- Wrote `services.yaml`: 4 groups, 7 services.
- **Issues found and fixed on the way:**
  - Proxmox links without `:8006` went to 443 and failed.
  - `ping` given as a URL (`http://10.10.10.21/`). `ping` takes a host only.
  - pfSense `siteMonitor` stayed red: the WebGUI was HTTP only and 443 was dropped. Fixed at the source by switching pfSense to HTTPS, see [[pfSense Configuration]] 2026-09-24.
- **Verification:** dashboard loads at `http://10.10.10.30:3000`, all configured services listed (checked through `/api/services`).
- **Pending:**
  - Phone access: Tailscale on `svc-01` or a subnet router for `10.10.10.0/24`.
  - `HOMEPAGE_ALLOWED_HOSTS` must get the Tailscale address once added.
  - claude-srv card: `href` to `https://claude.ai/code` once `claude-rc` runs (see [[claude-srv]]).
  - Optional: read-only Proxmox API token for live widgets, `settings.yaml` title/theme.
