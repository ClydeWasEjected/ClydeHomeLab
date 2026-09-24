# claude-srv

Related: [[Claude Server Design]] · [Homelab - Inventory](<../1 - Infrastructure/Homelab - Inventory.md>) · [[Proxmox Administration]]

## Current State

| Item | Value |
|---|---|
| Proxmox host / ID | `proxmox-a8`, CT 105 |
| Type | Unprivileged LXC, `nesting=1`, `/dev/net/tun` passed through (`dev0`) for Tailscale |
| OS | Debian 13 (`debian-13-standard_13.6-1`) |
| Resources | 2 cores, 2048 MB RAM, 512 MB swap, 16 GB rootfs on `local` |
| Network | `net0` on `vmbr1`, DHCP, currently `10.10.10.124` (no static mapping yet) |
| Start on boot | Yes |
| Timezone | Europe/Madrid |
| Users | `clyde` (sudo, NOPASSWD). Root SSH login disabled, password auth disabled. |
| Laptop access | `ssh clyde@10.10.10.124` with the laptop's `id_ed25519` key |
| Software | Claude Code (native installer, `~/.local/bin/claude`), Syncthing v2 (`apt.syncthing.net`, `stable-v2`), Tailscale, git, tmux |
| Syncthing | `syncthing@clyde` systemd service, GUI on `127.0.0.1:8384` only |
| Git | `~/vault`, remote `git@github.com:ClydeWasEjected/ClydeHomeLab.git`, key `~/.ssh/id_ed25519` (`claude-srv@homelab`), `core.autocrlf=input` |

Laptop side: Syncthing v2 unpacked to `%LOCALAPPDATA%\Programs\Syncthing`, started at logon by the `Syncthing` scheduled task, GUI on `127.0.0.1:8384`.

### Remote Control (planned, not running)

`claude remote-control` is Claude Code's server mode: it waits for sessions started from claude.ai/code or the Claude app. Planned as systemd unit `/etc/systemd/system/claude-rc.service`:

| Setting | Value |
|---|---|
| `User` | `clyde` (never root) |
| `WorkingDirectory` | `/home/clyde/vault` |
| `ExecStart` | `/home/clyde/.local/bin/claude remote-control --name claude-srv` |
| `Restart` | `on-failure` |
| `After` / `Wants` | `network-online.target` |
| `WantedBy` | `multi-user.target` |

No `--permission-mode bypassPermissions`: remote sessions keep asking before acting.

### Daily use

```bash
ssh clyde@10.10.10.124
tmux new -A -s claude      # attach if it exists, create if not
cd ~/vault && claude
# detach: Ctrl-b d  (session keeps running)
```

## Change Log

### 2026-09-23: Built

- Created CT 105 from the Debian 13 template, provisioned `clyde`, hardened `sshd` (no root, no passwords).
- Replaced Debian's Syncthing 1.29 with v2.1.5 from the official repo to match the laptop.
- Seeded `~/vault` with a byte-for-byte copy of the laptop vault including `.git`, so both sides started identical (no line-ending conflicts). `git status` clean after copy.
- Seeded `~/.claude/CLAUDE.md`, `global-memory/` and the homelab memory folder the same way.
- Paired Syncthing, added the three folders.
- **Verification:** all three folders idle with 0 errors on both sides. Laptop to server, server to laptop and delete propagation tested per folder.
- **Issue:** laptop to server changes in the memory folder never arrived. Cause: nested folder not seen by the Windows file watcher. Fixed with a 60 s rescan on the two Claude folders.
- Tailscale joined (`100.88.249.127`), GitHub deploy key `claude-srv` added with write access (first push `1b2fc47` succeeded), Claude Code logged in, Tailscale address added to the laptop's Syncthing device entry.
- **Pending:** pfSense DHCP static mapping for `10.10.10.124`.

### 2026-09-24: Remote Control design, Homepage card

- Chose `claude remote-control` as a systemd service over a dashboard button that runs commands. Homepage has no authentication, so a command button would let anyone on the LAN run it. Remote Control is authenticated by the Anthropic account.
- **Status:** unit file designed (see Current State), **not yet created**: `systemctl status claude-rc` returns "could not be found" (checked 2026-09-24).
- Added to the Homepage dashboard with `ping 10.10.10.124`. Note: `ping` from *inside* claude-srv fails (`Operation not permitted`, no `CAP_NET_RAW` in the unprivileged CT); pinging it from outside works.
