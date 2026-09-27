# Hermes Dashboard

Related: [[Hermes Dashboard Design]] · [[Hermes]] · [[Homepage]] · [[svc-01]] · [[claude-srv]]

## Current State

```mermaid
flowchart LR
    subgraph cs["claude-srv ~/dashboard (data)"]
        g["sync_google.py · 30 min<br/>Calendar + Gmail via claude -p"] --> pub
        b["build.py · 1 min<br/>git, systemd, TCP checks,<br/>Hermes reports, Career.md"] --> pub["public/*.json<br/>public/logs/*.txt"]
        pub --> r["brief.py · 10 min<br/>(skipped if nothing changed)"]
        r --> pub
        st["statusline.py<br/>(interactive sessions)"] --> pub
        pub --> h8["serve.py :8095"]
    end
    subgraph sv["svc-01 (page)"]
        ts["tailscale serve :443"] --> n["nginx 127.0.0.1:80 · container hermes<br/>/ = index.html · /data/ → claude-srv:8095 (Tailscale IP)"]
    end
    h8 --> n
    you(["💻 📱 browser<br/>Tailscale only"]) --> ts
```

| Item | Value |
|---|---|
| URL | `https://svc-01.tailfdea8b.ts.net` (Tailscale only, `tailscale serve` on svc-01). Not reachable from the LAN |
| Page | svc-01 `~/hermes/`: `docker-compose.yml` (`nginx:alpine`, container `hermes`, `127.0.0.1:80:80`), `nginx.conf` (`/data/` → `100.88.249.127:8095`), `site/index.html` |
| Page source | claude-srv `~/dashboard/site/index.html`, `~/dashboard/svc-01/` (copied to svc-01) |
| Data | claude-srv `~/dashboard/`: `build.py`, `brief.py`, `sync_google.py`, `statusline.py`, `config.json`, output in `public/` |
| Refresh | Page polls every 15 s, header shows **Live** / **Offline** (no data for 45 s) |
| Not in git | `~/dashboard` (and `~/hermes-mail`) live only on claude-srv |

### systemd units (claude-srv, system units unless noted)

| Unit | Schedule | Does |
|---|---|---|
| `dashboard-build.timer` / `.service` | every minute | `build.py` → `dashboard.json`, `logs/*.txt`. `User=clyde`, `SupplementaryGroups=systemd-journal` |
| `dashboard-brief.timer` / `.service` | every 10 min | `brief.py`: Claude writes `brief.json` (skipped when the data hash is unchanged, at least once a day) and `lesson.json` (once per new lesson) |
| `dashboard-google.timer` / `.service` | every 30 min, 07:00 to 01:30 | `sync_google.py`: `claude -p` limited to Calendar `list_events` and Gmail `search_threads` → `calendar.json`, `mail.json` |
| `dashboard-ticks.service` | always | `ticks.py`: shared errand ticks, `GET`/`POST /ticks` on `100.88.249.127:8096`, published by nginx as `/api/`. Writes only `~/dashboard/state/ticks.json` (`ReadWritePaths`) |
| `dashboard-http.service` | always | `serve.py` on `100.88.249.127:8095` (Tailscale IP only). Read-only, answers only its own Host names (421 otherwise), serves only `.json`, `.txt` and `.html` under `public/`, no directory listing, 10 s client timeout. Sandboxed (systemd exposure 1.4), `After=tailscaled.service` |
| status line (`~/.claude/settings.json`) | on redraw | `statusline.py` → `usage.json` |

### Page layout (top to bottom)

| Section | Shows | Source |
|---|---|---|
| Top bar | Quick links, Live dot, clock | `config.json` `links` |
| Hero | Greeting, situation message, alert | `brief.json` (`greeting`, `message`, `alert`) |
| The one thing | Single most valuable action, why, minutes, Mark done | `brief.json` `one_thing` |
| KPIs | The road, Streak, Lab, Fortune, Claude usage | `build.py`, `usage.json` |
| Briefing (5/12) | Situation by topic: Today, Inbox, Career, Lab, Security, Money, Last done | `brief.json` `briefing` |
| Errands (7/12) | One prioritised list, Today / Soon, area tag, minutes, tick off, progress bar | `brief.json` `errands` + `reminders.json` |
| Upcoming (5/12) | Next 7 days of events, reminders count | `calendar.json`, `reminders.json` |
| Messages (7/12) | Up to 8 inbox threads that matter, category, "reply" tag, unread count, link to Gmail | `mail.json` |
| Fortune (5/12) | Pipeline bar, live processes, follow-ups due (7 to 21 days), reply rate | `Career.md` `## Job search log` via `build.py` |
| The road (7/12) | Phase stepper, all 8 phases with bar and note, cert path | Latest Hermes morning report `phases`, `config.json` `certs` |
| Sentinels (6/12) | Tabs: Hosts (TCP check + latency), Scripts (tap for log summary), Watchdogs | `config.json` services, systemd `UNITS`, Proxmox API journal |
| Wins (6/12) | Highlights (48 h), day-by-day commits (5 days), 26-week heatmap | `brief.json` `wins`, `build.py` `daily`, `heatmap` |
| Wisdom (12/12) | Quote, excerpt, key ideas, For you today; the idea, story, why, 3 actions, watch out; reflection question | `lessons.json` via `build.py`, `lesson.json` |

Ticks (errands, the one thing) are keyed by a hash of the task text and stored on claude-srv (`ticks.py`), so every device shows the same ones. The browser keeps an offline copy and queues ticks made while offline. Ticks older than 30 days are forgotten. Phone: one column in the same order.

### Data formats for other tools

```jsonc
// public/calendar.json  (written by sync_google.py)
{"source": "Google Calendar", "at": "25/09 07:00", "events": [{"title": "Interview Acme", "start": "2026-09-26T10:00:00+02:00", "end": "...", "location": "Teams", "all_day": false}]}
// public/mail.json  (written by sync_google.py)
{"at": "25/09 07:00", "unread": 201, "items": [{"from": "...", "subject": "...", "summary": "...", "category": "job|admin|money|personal|lab|other", "needs_reply": true, "date": "...", "url": "https://mail.google.com/..."}]}
// public/reminders.json  (no source yet)
{"items": [{"text": "Rearm DC01 eval", "due": "2026-11-15T09:00:00+01:00", "done": false}]}
```

### Watchdog feed: read-only Proxmox token (to do, Clyde)

`build.py` reads the A8 journal through `GET /api2/json/nodes/proxmox-a8/journal`. The token needs `Sys.Syslog` only: it can read logs, nothing else. The A8 certificate is self-signed, so `build.py` pins its SHA-256 fingerprint (`config.json` `watchdogs.fingerprint`) and refuses to send the token if it changes.

```bash
# on proxmox-a8
pveum role add DashboardLog -privs Sys.Syslog
pveum user add dashboard@pve --comment "Hermes dashboard, read-only journal"
pveum acl modify /nodes/proxmox-a8 -user dashboard@pve -role DashboardLog
pveum user token add dashboard@pve feed --privsep 0      # prints the secret once
# on claude-srv
echo 'dashboard@pve!feed=<secret>' > ~/.config/pve-dashboard.token && chmod 600 ~/.config/pve-dashboard.token
```

Check the pinned fingerprint against the Proxmox GUI (node, System, Certificates) before trusting it.

### Playbook pages (phase exercises)

Phase exercises you can follow without Claude, in three levels like an academy: **hub** (`playbook.html`, all phases with progress) then **phase** (`?p=c4`, its modules) then **module** (`?p=c4&s=s2`, learn first, then do). Data is one JSON per phase in `~/dashboard/public/playbooks/<id>.json`, plus `index.json` (tracks A to H with status and note, and the items inside a track). A new phase is a new JSON and one line in `index.json`, no page change. Link "Playbook" in `config.json`.

| Level | Shows |
|---|---|
| Hub | The whole road A to H: roadmap strip with each phase's status, Continue card, a card deck for phases that have items (Phase C: C1 shown as done, C4, C4b, C5 with progress, C3, C2, C6, C7 dimmed as not written yet), and a row per remaining phase ("No playbook yet"). Statuses come from `index.json` `tracks`, copied from the README roadmap: edit that file when a status changes |
| Phase | Goal and outcome, progress ring, Continue card, module list with per-module bar, Blueprint and Facts, reference tabs (Concepts, When it does not work, Cheat sheet, Stuck and beyond) |
| Module | Course index sidebar (check marks, current highlighted; a scrolling chip row on the phone), "Learn first" lesson, "Do" steps fully expanded (host chip that links to the Proxmox console, where in GPMC, values, commands with Copy, example output, what you should see, watch out), done steps fold away, "Done when", previous and next module |

Notes and documentation: every step has a "Your output" box (saved as you type via `POST /api/notes`, secret-looking values masked on the server). The phase page has a Documentation card: **Request documentation** sets `state/ready/<id>.json`, `dashboard-docs.timer` (every 3 min, no Claude call unless requested) runs `docs_draft.py`, which asks Claude (sonnet, no tools, notes treated as untrusted data) for the vault-format documentation and stores it in `state/drafts/<id>.md`. The draft is shown on the page. Publishing into the vault is a separate step: tell Claude "publish <code> docs" and it checks the values against the live systems and writes the files. Targets per playbook are in the JSON field `docs`. Screenshots are pasted into the same box with Ctrl+V (also drag and drop, or the Add image button), shrunk in the browser (max 1600 px wide) and saved by `POST /api/shot` as `state/shots/<id>/<step>-<n>.png`; only real PNG or JPEG is accepted (never SVG), 3 MB each, 40 per playbook. The drafter cannot see images: it only refers to them by file name, and the images are looked at during the publish step. Files: `~/dashboard/state/{evidence,ready,drafts,shots}` (mode 600, not served, not in git).

Progress reuses the ticks API (`api/ticks`, key = hash of `pb:<id>:<step id>`), shared with the errands, so laptop and phone agree and offline ticks queue. Playbook ticks are permanent (the page sends `keep: true`, see the 2026-09-26 entry below); errand ticks still expire after 30 days. Nothing here calls Claude: it keeps working when Claude usage is exhausted.

JSON fields. Phase: `id`, `code`, `title`, `phase`, `summary`, `level`, `tags`, `after`, `goal`, `outcome`, `hosts`, `facts`, `concepts`, `blueprint`, `stages`, `trouble`, `cheat`, `sources`, `stuck`, `next`. Stage: `id` (`s0`..), `title`, `min`, `why` (one line), `learn` (paragraphs), `steps`, `done_when`. Step: `id`, `text`, `host`, `where` (object: `app`, `open`, `title`, `nav` list, `then`, `opens`, `not`), `do` (numbered actions), `path` (plain text or a `Computer Configuration > ...` trail), `values`, `cmd`, `cmdhost`, `sample`, `expect`, `why`, `warn`. Module: also `tools` (list of `host`, `name`, `how`: the windows used in that module). Every GUI step must have `where` and `do`.

### Pending

- **Multi-account Gmail:** the claude.ai Gmail connector holds one Google account at a time, so Messages and the inbox briefing see only `clyde.john253`, not `clyde.jcaiga`. Plan: a self-hosted multi-account Gmail MCP server on claude-srv (preferred over third-party services like Composio, which would hold mailbox access), read-only scopes for the dashboard sync.
- Reminders source.
- Read-only Proxmox token for the Watchdogs tab (below).

### Operations

| Task | Command |
|---|---|
| Change hosts, links or cert states | Edit `~/dashboard/config.json` on claude-srv (live within a minute) |
| Add an automation | One line in `UNITS` in `build.py` |
| Add a name or IP the data or tick server is reached by | Edit `HOSTS` in `~/dashboard/serve.py` (data) or `ticks.py` (ticks), then `sudo systemctl restart dashboard-http dashboard-ticks`. A name not in the list gets `421 Misdirected Request` |
| Deploy a page change | `scp ~/dashboard/site/index.html adm-jnclyde@10.10.10.30:hermes/site/` (no restart needed) |
| Rebuild data now | `sudo systemctl start dashboard-build.service` |
| Force a new briefing | `rm ~/dashboard/brief.hash && sudo systemctl start dashboard-brief.service` |
| Sync calendar and mail now | `sudo systemctl start dashboard-google.service` |
| Page logs (svc-01) | `cd ~/hermes && docker compose logs -f hermes` |
| Data job logs (claude-srv) | `journalctl -u dashboard-build -u dashboard-brief -u dashboard-google -n 50` |

## Change Log

### 2026-09-25: Built (replaces the Hermes panel inside Homepage)

- Clyde's feedback on the panel: badly separated, generic, only used the middle of the screen, cut off on the phone, and Homepage's own tiles still looked default there (phone cached the old `custom.css`).
- Built a standalone full-screen page: top bar (quick links, clock), hero (greeting, alert, 4 stats), roadmap stepper, three columns Today / Briefing / Lab, single column on the phone.
- New features: live host checks with latency, 12-week commit heatmap, today's tasks you can tick off, lesson of the day, activity timeline, job search kanban, cert path.
- `build.py`: added `services`, `heatmap`, `today`, `lesson`, `links`, `certs`. New `config.json`. `brief.py` hash now includes host up/down.
- svc-01: new `nginx:alpine` container `hermes` on `:80`, proxies `/data/` to claude-srv `:8095`.
- Homepage: Hermes iframe group and its `layout` entry removed (backup `~/homepage/services.yaml.bak-20260925b`). Homepage keeps the gold theme.
- **Issue:** first host checks read ~37 ms for every host, localhost included: thread scheduling noise from checking in parallel. Made sequential, now 0 to 3 ms.
- **Verification:** `http://10.10.10.30/` 200 with `Cache-Control: no-cache`, `/data/dashboard.json`, `/data/brief.json` and `/data/logs/claude-rc.txt` 200 through the proxy. Host checks: pfSense, both Proxmox nodes, claude-srv, svc-01 up; DC01 and WIN11-01 down (VMs off). Visual check on desktop and phone: pending (Clyde).

### 2026-09-25: Redesign, usage bar, watchdogs, calendar and reminders

- Clyde's feedback: text too small, too much information, name and description ran together in the Lab list ("pfSenseFirewall": both were inline spans). References: Muzli "best dashboard design examples 2026" (surface the key figures, minimal noise, drill down for detail) and Dribbble phase/stepper UIs.
- Bigger type everywhere (base 15.5 px, KPIs 44 px serif). Fewer items visible: pending shows the top 3 with "Show all", automation log summaries open on tap, Hosts / Automations / Watchdogs merged into one Systems card with tabs. Roadmap stepper redrawn: larger diamonds, current phase with a halo, detail line with the phase percentage.
- New: Claude usage bars (status line hook), KPI row, Upcoming and Reminders cards (empty state until the calendar MCP writes their files), Watchdogs tab (Proxmox API, pinned certificate).
- `~/.claude/settings.json` on claude-srv: `statusLine` runs `~/dashboard/statusline.py`. Not synced to the laptop (Syncthing only takes `CLAUDE.md` and `global-memory` from `~/.claude`).
- **Verification:** status line script tested with sample input, then a live interactive session wrote real values within seconds (5-hour 14 %, weekly 17 %). Proxmox journal call reaches the API and is refused with `401 no such user`, as expected before the token exists. Page 200. Visual check: pending (Clyde).

### 2026-09-25: Layout fixes, stale usage

- Greeting used a narrow column (5 lines): hero now gives it 2.2 of 3.2 parts of the width, balanced wrapping, and `brief.py` caps it at 12 words. Pending items are 12 words max, each in its own rounded box with a numbered circle.
- **Issue:** usage bar showed 14 % while `/usage` said 80 %. Cause: the status line only runs in interactive sessions and the tmux ones were idle; Remote Control sessions (where the usage happened) never run it. The bar now fades and says "stale" when the reading is older than 20 minutes. Reading usage through the account's OAuth token was considered and rejected by Clyde.
- Left column looks empty until the calendar and reminders are connected: accepted as is.

### 2026-09-25: Detailed lesson card

- The lesson card showed only the quote and book, off-centre next to the email's full version. `build.py` now passes `idea`, `chapter`, `excerpt`, `key_points`; the card has a centred header (ornament, quote, book, idea), the excerpt, numbered key ideas and a "For you today" box.
- Usage bar is not real time: the page polls every 60 s, but the value only changes when an interactive Claude Code session on claude-srv redraws its status line.

### 2026-09-25: Real time, lesson study, number circles

- **Real time:** page polls every 15 s (was 60), data rebuilt every minute (was 5 min), briefing checked every 10 min (was 30, still skipped when nothing changed). Header shows a pulsing **Live** dot that turns red "Offline" if no data arrived for 45 s. Clock ticks every second. Exceptions: phases and today's tasks change once a day (Hermes morning report), Claude usage only when a terminal session redraws.
- **Lesson study:** `brief.py` asks Claude once per new lesson for a deeper study (idea, story from the book, why it works, 3 actions for this week, watch out, reflection question), cached in `public/lesson.json` by a hash of book + quote. Prompt forbids invented quotes and unattributed examples. First study (Law 25) used George Sand, which is the book's own example.
- **Issue:** numbers in the pending circles sat low. Cause: Cormorant Garamond uses old-style figures (3, 4, 5 descend below the baseline). Circles now use Inter lining figures.
- Timers edited in `/etc/systemd/system/dashboard-{build,brief}.timer`.

### 2026-09-25: Redesign around Hermes as a guide

- Clyde's feedback: space badly distributed (lesson card too long in one column, others cramped), briefing felt like a reminder list duplicating Today, wanted it useful and personal, backed by research, with Hermes as a persona.
- Research used: Stephen Few (dashboard = most important information at a glance), progressive disclosure (summary, context, details), Amabile and Kramer's progress principle, Zeigarnik and goal-gradient effects, Hermes mythology (god of crossings, roads, herms, trade, luck).
- New layout: hero (Hermes message + **The one thing** with Mark done), 5 KPIs, **Errands** (7/12) + **Fortune** (5/12), **The road** full width with cert path, **Sentinels / Wins / Upcoming** in thirds, **Wisdom** full width in two columns. Phone: one column in priority order. Activity timeline replaced by Wins; Today, Briefing and Reminders merged into Errands.
- `brief.py`: new persona and schema (`message`, `one_thing`, `errands` with area and when, `wins`), jobs summarised instead of the full 75-row list, date in the hash so errands are re-planned daily.
- `build.py`: jobs `total`, `reply_rate`, `this_week`, `live`, `follow_up` (no reply for 7 to 21 days, oldest first); heatmap 26 weeks.
- Ticks (errands and the one thing) are stored in the browser per task text, so they survive a rewritten briefing.
- **Verification:** first run of the new briefing: one thing = a time-sensitive career decision, 7 errands without duplicates, 4 wins. Page 200, script brackets and template literals balanced. Visual check: pending (Clyde).

### 2026-09-25: Briefing card back, equal-height rows

- Clyde wants a briefing on the general dashboard, separate from the errands. `brief.py` adds `briefing` (4 to 5 topics: Last done, Lab, Career, Security, Automations; situation only, tasks stay in errands). New layout rows: Briefing 5/12 + Errands 7/12, Fortune 5/12 + The road 7/12.
- Gaps under short cards fixed: grid rows now stretch so cards in a row share a height; Upcoming lays out in two columns when it is full width.
- First briefing flagged a stale item: the morning report still carries the "duplicate DC01" task although it was closed on 2026-09-24.

### 2026-09-25: Phase details and daily wins

- The road and Wins cards had empty space once rows share a height. The road now lists all 8 phases under the stepper (progress bar, state, Hermes's note; click a step or a row to highlight). Wins adds "Day by day": last 5 days with commits, count and the first 3 subjects. `build.py` adds `daily` (7 days).
- Homepage became the lab-only dashboard in the same style, see [[Homepage]].

### 2026-09-25: Google Calendar and Gmail

- Claude.ai connectors (Gmail, Google Calendar) only work inside a Claude session, so `sync_google.py` asks `claude -p` with `--tools ""` and `--allowedTools` limited to calendar `list_events` and Gmail `search_threads`: nothing can send, delete or edit. The prompt treats email subjects and snippets as untrusted data; the page escapes all of it and only links to `https://mail.google.com/`.
- `build.py` adds `mail`; `brief.py` gets calendar and mail (without sync timestamps in the hash), Hermes now briefs on the day as well as the lab (Today, Inbox, Career, Lab, Security, Money) and turns emails needing a reply into errands.
- Layout: Upcoming 5/12 + Messages 7/12 right after Briefing and Errands; Sentinels and Wins share the row after The road.
- **Verification:** first sync 23 s: 0 events (calendar confirmed empty for 2 weeks by a direct query), 8 mail items (2 flagged for reply), 201 unread. Briefing written with 6 topics, one thing = a time-sensitive career decision.
- **Privacy:** the page now shows email senders and one-line summaries to anyone on the LAN. Another reason never to expose `:80`.

### 2026-09-25: Tailscale only, one HTTPS name (security audit H2)

- **Problem:** the page, `/data/` (mail summaries, job pipeline, calendar) and claude-srv `:8095` (directory listing) were readable without auth from anything on the flat LAN, WiFi included. Also the iPhone home-screen web app only worked at home (`10.10.10.30`) or with the raw `100.x` IP.
- **Changed (Clyde):** HTTPS certificates enabled in the tailnet. svc-01: `hermes` published on `127.0.0.1:80:80` only, `tailscale serve --bg http://127.0.0.1:80` in front (tailnet-only HTTPS). claude-srv: `http.server` bound to its Tailscale IP, `After=tailscaled.service`; nginx `/data/` and Homepage `services.yaml` point to `100.88.249.127:8095`. iPhone web app re-added from the new URL, VPN On Demand on.
- **Issues:** `"127.0.0.1:80"` (missing container port) gave `invalid hostPort`, so compose kept the old container. `sed -i` on the single-file bind mount `nginx.conf` replaces the inode, so the running container kept the old file: `--force-recreate` needed. Laptop browser showed `DNS_PROBE_POSSIBLE` while Windows resolved the name: Secure DNS (DoH) bypasses MagicDNS, set to the current provider.
- **Verification:** from the LAN (claude-srv `10.10.10.124`): `10.10.10.30:80` and `10.10.10.124:8095` refused. Through Tailscale: page and `/data/dashboard.json` 200 from claude-srv, iPhone (mobile data) and laptop.
- **Open:** Homepage `:3000` still on the LAN (lab data only). No auth inside the tailnet: Tailscale ACLs in the firewall phase.

### 2026-09-25: Stable errand text (ticks survive a new briefing)

- **Problem:** ticks are stored per errand text, and `brief.py` rewrote the briefing 33 times in one day, rewording errands each time, so ticks vanished on reload.
- **Changed:** `brief.py` `current_errands()` passes the last briefing's errands and one thing into the prompt; new rule: a pending item keeps its text exactly, done items are dropped, new items only for new facts. Previous errands are not in the hash (that would force a rewrite every run). Backup: `brief.py.bak-20260925`.
- **Verification:** two forced briefings in a row: no errand reworded, only reordered; one item dropped.
- **Open:** ticks per browser, fixed in the next entry.

### 2026-09-25: Ticks shared across devices

- **Problem:** a tick on the phone didn't show on the laptop: ticks lived only in each browser's `localStorage` (the page was read-only while it was open to the LAN).
- **Changed:** new `~/dashboard/ticks.py` (stdlib `http.server`) with `dashboard-ticks.service`, bound to the Tailscale IP, port 8096. `POST` only accepts JSON from the dashboard's own origin (a cross-site JSON post needs a CORS preflight, never answered), a key matching the page's hash format, `done` as a boolean, body up to 200 bytes; keys only, never task text. svc-01 nginx: `location /api/` → `100.88.249.127:8096`, `client_max_body_size 1k` (backup `nginx.conf.bak-20260925`). Page: ticks load from `api/ticks` every 15 s, a tick is saved at once, offline ticks queue in `localStorage`; the first visit from each browser uploads the ticks it already had.
- **Verification:** local test of every rejection (wrong origin 403, `text/plain` 415, bad key and non-boolean 400, 300-byte body 413, invalid JSON 400). Through `https://svc-01.tailfdea8b.ts.net/api/ticks`: tick and untick 200. From the LAN, `10.10.10.124:8096` refused. Page JS not browser-tested on claude-srv (no browser there): cross-device check by Clyde.
- **Issue (same day):** unticks looked lost. A tick made during a running sync waited for the next 15 s cycle, iOS paused the web app's timers in the background, and a request cut off by a locked phone could leave the sync stuck. Fixed: 5 s fetch timeout, a second sync pass right after a tick made mid-sync, immediate refresh when the page becomes visible. `ticks.py` now logs `tick`/`untick <key>` per write (`journalctl -u dashboard-ticks`). Page backup: `site/index.html.bak-20260925-ticks`.
- **Open:** Hermes still can't see ticks (`brief.py` could read `ticks.json` and drop ticked errands).

### 2026-09-25: Security page
- **Changed:** new page `security.html` next to `index.html` (same style), linked as "Security" in the link bar (`config.json`). It shows the posture at a glance (urgent, open, fixed, work left, trend), a "Do next" queue, what changed, findings grouped by machine in plain language (tap for why, how and how it gets checked), and the weekly reports.
- **Why:** finding codes like "H1" or "M4" meant nothing on a phone. Security dashboards group by asset, show direction over time, and put "what needs attention" first.
- **Data:** `~/dashboard/public/security.json` (tailnet-only via `/data/`). Report copies are in `public/reports/`. The real report files stay out of this public repo.
- **Verification:** over Tailscale: page, data and report all return 200. Visual check on the phone: pending (Clyde).

### 2026-09-26: Lower Claude usage
- **Found:** in 24 hours `brief.py` called Claude 39 times (12 more calls failed on the session limit) and `sync_google.py` about 38 times, all on the default model. Each briefing prompt is about 34k characters.
- **Changed:** `brief.py` runs on `--model sonnet` (briefing and lesson study) and rewrites at most once per 45 min, even when facts change. `sync_google.py` runs on `--model haiku` and syncs at most once per 55 min (`--force` to override); the timer still fires every 30 min and skips. Hermes emails keep the default model (2 a day, quality matters). Backups: `*.bak-20260926`.
- **Verification:** forced Google sync on Haiku: 8 mail items, 1 event, and the next run skipped. Test briefing on Sonnet: valid JSON with all fields, same voice.

### 2026-09-26: Playbook page (C4 Group Policy)
- **Why:** Clyde could not continue a lab phase without Claude because "C4 GPOs" had no concrete rules or steps anywhere (only proposed password values in memory). Built the whole C4 exercise as a page in the dashboard: 8 stages, 32 steps, about 3.75 h, five GPOs (Default Domain Policy, Workstation-Baseline, Local-Admins, Operations-Restrictions, Security-PSLogging), each tested where it applies and where it must not.
- **Design:** data-driven (`playbooks/c4.json`) so C4b LAPS, C5 and later phases only need a new JSON. Same palette as the other pages. Layout follows progressive disclosure (Next up first, detail on tap) and the goal-gradient effect (progress ring, per-stage bars). Rules come from CIS Level 1 and the Microsoft Security Baseline, each with a one-line why.
- **Files:** claude-srv `~/dashboard/site/playbook.html` (copied to svc-01 `hermes/site/`), `~/dashboard/public/playbooks/c4.json`, link added to `config.json` (backup `config.json.bak-20260926-pb`).
- **Verification:** JSON valid (32 unique step ids), page script checked for balanced brackets and template literals, every `getElementById` target exists. From svc-01: page, `/data/playbooks/c4.json`, `/data/dashboard.json` (link present) and `/api/ticks` all 200. **Not verified:** no browser or JS runtime on claude-srv, so the page has not been executed. Visual check on desktop and phone: pending (Clyde).

### 2026-09-26: Playbooks become an academy (hub, phase, module) plus C4b and C5
- **Why:** Clyde asked whether the first C4 page was the full exercise or compacted for the dashboard, and wanted a Moodle or Hack The Box style structure. Honest answer: the first version was a runbook with one-line reasons, compacted to fit cards. A module page has room for the lesson, so every stage now has a `learn` section (how it works, why these values, the attacker view for Phase G, known traps) and several steps have example output.
- **Changed:** `playbook.html` rewritten as three views (hub, phase, module) driven by the URL, back button works. Existing C4 ticks keep working (same keys). Backup of the single-page version: `playbook.html.bak-20260926-v1`.
- **New content:** `c4b.json` Windows LAPS (7 modules, 25 steps) and `c5.json` file shares and NTFS (8 modules, 33 steps), `index.json` with C3, C2, C6, C7 as planned. C4b commands and setting names were checked against Microsoft Learn (Windows LAPS docs): the decryption principal is a policy setting, not a cmdlet, and the cmdlets need the April 2023 update on DC01 (Server 2022 Evaluation), so that is a preflight step.
- **Decision (C5):** shares go on a new member server FS01 in a new OU `Servers`, not on DC01 (a DC should not serve files). FS01 IP suggested `10.10.10.25`: `10.10.10.23` is the main PC. The playbook explains the trade-off and the written-exception fallback.
- **Verification:** all three JSON files valid, step ids unique, every field the page reads exists, page script checked for balanced brackets and template literals, every `getElementById` target exists. From svc-01: page, `index.json`, the three playbooks and `/api/ticks` return 200. **Not verified:** the page has never run in a browser (no browser or JS runtime on claude-srv), and the C4b and C5 commands were not run against a real domain. Expect small mistakes (a wrong cmdlet parameter, an off menu name): report them and they get fixed. Visual check: pending (Clyde).

### 2026-09-26: Hub shows the whole roadmap
- **Why:** Clyde pointed out that C1 is done and that A and B exist, so a hub showing only the new Phase C playbooks hid the real progress.
- **Changed:** `index.json` is now `tracks` A to H (status and note from the README roadmap: A in progress, B and D started, C in progress, E to H pending) with Phase C's items inside, C1 marked done (2026-09-24). The hub has a roadmap strip, the Phase C deck and a row per phase that has no playbook yet. Backup of the previous page: `playbook.html.bak-20260926-v2`.
- **Open:** A and B are in progress but have no playbook. The statuses are the vault's; if A or B are further along than the README says, edit `index.json` (or update the README, then this file). Not run in a browser, same caveat as above.
- **Issue (same day):** cards for C4, C4b and C5 were not clickable. Cause: I changed `index.json` from `items` to `tracks` but the loader still read `IDX.items`. It threw inside a `try` with an empty `catch`, no playbook loaded, and every card fell back to a non-link "unavailable" tile. The bracket and id checks cannot see a data-shape mismatch. Fixed the loader, and load errors now show in the page footer ("Load problem: ...") instead of being swallowed.
- **Lesson:** when a data file changes shape, grep every consumer of it. A real browser test would have caught this immediately: worth installing a headless browser on claude-srv if Clyde agrees.

### 2026-09-26: Playbook ticks never expire
- **Why:** Clyde does not want to worry about progress vanishing after 30 days. The tick server forgot every tick older than 30 days, which is right for errands and wrong for a multi-week phase.
- **Changed:** `ticks.py` accepts an optional `"keep": true` on `POST /ticks` (must be a boolean, else 400). Permanent ticks are stored with a `keep:` prefix and skip the 30-day cleanup; they are capped at 2000 so the file cannot grow without limit. Errand ticks (no `keep`) behave as before. The playbook page sends `keep: true` on every tick and, once per playbook per browser, re-sends the ticks made earlier as permanent (only after it has read the server's list). Backups: `ticks.py.bak-20260926`, `playbook.html.bak-20260926-v3`.
- **Verification:** unit test of the cleanup (a 400-day-old permanent tick kept, a 400-day-old errand tick dropped). Live on `:8096`: permanent tick stored, `keep: "yes"` rejected 400, an old-style post without `keep` still accepted, test keys removed, the 4 existing ticks untouched. Page checked statically and served; not run in a browser.
- **Note:** ticks made on a device that never opens the page again stay temporary until it does.

### 2026-09-26: Security audit fixes (data server, ticks, units)
- **Found (audit):** the data server answered any `Host` header (a website open on a tailnet device could read the data through DNS rebinding), listed directories and named its Python version.
- **Changed:** `python3 -m http.server` replaced by `~/dashboard/serve.py`: Host allow-list, `.json`/`.txt`/`.html` only, no dotfiles, 404 for directories, neutral `Server` header, 10 s timeout. `ticks.py` got the same Host check and timeout. Both units sandboxed (capabilities, kernel, namespaces, syscall filter): `systemd-analyze security` 8.4 to 1.4. nginx sends the Tailscale IP as Host, so the page path is unchanged. Backups: `dashboard-http.service.bak-*`, `dashboard-ticks.service.bak-*`, `ticks.py.bak-20260926`.
- **Verification:** requests with a foreign Host return 421 on both ports; `/`, `/logs/`, `/reports/`, `/playbooks/` return 404; traversal attempts 404; through svc-01 the page, all data files, the log and report files and `/api/ticks` return 200, and a tick written through nginx is saved.
- **Note:** the security report itself is not kept in this repo.

### 2026-09-26: Security practice track (S1)
- **Why:** Clyde asked how companies run security and how to keep patched. Playbook `sec1` (6 modules, 30 steps): the vulnerability management loop, rating findings, fixing one safely (svc-01 SSH), patching with a schedule, making it a process, and writing the weekly check script himself (spec and checkpoints, no code from Claude). The Concepts tab doubles as a glossary. Written process: [[Security Process]].
- **Changed:** `index.json` has a cross-cutting track `S` (optional `label` field for the heading, otherwise "Phase X"). Backup of the page: `playbook.html.bak-20260926-v4`.
- **Verification:** all four playbooks and the index pass a strict field check (every field the page reads), page script bracket check, and pages return 200 from svc-01. Not run in a browser.

### 2026-09-27: Notes on every step and automatic documentation drafts
- **Why:** Clyde wanted to paste outputs into the playbook while working, and have the documentation written when he finishes, instead of collecting notes and sending them by chat.
- **Changed:** `ticks.py` gained `GET/POST /notes`, `POST /ready` and `GET /draft` (same Host and origin checks; per-route body limits; masks secrets, private keys and tokens before saving; only known playbooks and step ids). svc-01 nginx: `location = /api/notes` with `client_max_body_size 64k` (config backup `nginx.conf.bak-*`, recreated with `--force-recreate`). New `docs_draft.py` with `dashboard-docs.service` and `.timer` (sandboxed, exposure 4.0, shared `llimit.py` cooldown, one call per request, three attempts). Page: notes box per step, Documentation card, no re-render while typing, unsaved text is flushed on blur and when the tab is hidden. Backups: `ticks.py.bak-20260927`, `playbook.html.bak-20260927-notes`.
- **Design choice:** the drafter has no tools and only writes `state/drafts`, never the vault. The vault is a public repo, so publishing stays a reviewed step.
- **Verification:** 17 route tests on a spare port (masking, wrong step, wrong origin, wrong Host, too long, empty deletes, ready and draft flow); through nginx a 5 KB note saved and read back, a 70 KB body is refused with 413; full end-to-end run through the sandboxed service on a throwaway playbook with a fake password and a prompt injection in the notes: draft in the vault format, no secret, injection ignored, missing evidence listed as "Not evidenced", no dashes, file mode 600. Test files removed. **Not verified:** the page in a real browser.

### 2026-09-27: Pasted screenshots
- **Why:** Clyde wanted to paste screenshots into the playbook, not attach files.
- **Changed:** `ticks.py` `POST /shot` (base64 PNG or JPEG, magic bytes checked, size and count caps, names never reused) and `GET /shot`; nginx `location = /api/shot` with a 5 MB body limit (config backup `nginx.conf.bak-*`); page: Ctrl+V, drag and drop and an Add image button on every step box, thumbnails with remove, client-side shrink. `docs_draft.py` lists screenshot file names per step and is told it cannot see them. Backups: `ticks.py.bak-20260927-shots`, `docs_draft.py.bak-20260927`, `playbook.html.bak-20260927-shots`.
- **Verification:** 17 server tests on a spare port (hostile inputs: SVG, script disguised as an image, bad base64, oversize, path traversal in the name and in delete, wrong origin, foreign Host); through nginx a real PNG saved, came back as `image/png`, oversize was refused with 413 and the test image was removed. **Not verified:** paste, drop and the browser-side shrink in a real browser (no browser on claude-srv).
- **Note:** screenshots can show secrets. They stay private on claude-srv and reach the vault only when picked during publishing.

### 2026-09-27: Clearer steps (Where panel, numbered actions, machine colours)
- **Why:** Clyde kept losing track of where to do things (wrong GPO editor, Policies instead of Preferences, wrong machine). The steps said what to do but not where.
- **Changed:** every step shows a **Where** panel: the machine (a coloured chip: DC01 gold, WIN11-01 blue, FS01 green, svc-01 purple, claude-srv amber, Proxmox orange), the program, the exact window title to check, the tree path as a trail whose last item is highlighted, what happens next, and a red "Not here" line for the usual wrong turn. Below it a numbered **Do this** list, then the values, then the commands (labelled "Run in PowerShell on DC01"), then expected result and warning, with the reasoning last. Each module starts with a **Windows you will use** card, and each Do card starts with the rule "machine, program, window title". Older steps whose path is a plain `Computer Configuration > ...` string turn into a trail automatically. C4 (13 steps and 8 modules), plus the GUI steps of C4b and C5, were rewritten. Backup of the page: `playbook.html.bak-20260927-where`.
- **Rule for new playbooks:** no GUI step without `where` and `do`. Name the window title, mark the wrong turn.
- **Verification:** static bracket check, strict field check on all four playbooks, pages 200 from svc-01. Not seen in a browser.

### 2026-09-27: Where panel v2, stale-page guard and a real page test
- **Why:** Clyde reported the Where part was gone. Most likely his browser ran the previous page script against the new data: the old script only understands `path`, which had been removed from steps that now have `where`. He also asked for it to be clearer.
- **Changed:** the Where panel is now a coloured card (edge colour = machine): the machine and program, "1. Open it", "2. Check the title" as a mock window title bar to compare with the real window, "3. Go to" as an indented folder tree with the destination highlighted ("you end up here"), then what to do, the expected result and a red "Not here" line. Steps with `where` also keep a plain `path` string as a fallback for an old cached page. New guard: the page has `PAGE_VERSION` and `playbooks/index.json` has `page`; when they differ the page reloads itself once and otherwise shows an "out of date" banner. **Deploy rule:** bump both together whenever `playbook.html` changes. Backup: `playbook.html.bak-20260927-where2`.
- **Test:** installed `quickjs` (1.9 MB, apt) on claude-srv. `qjs --std ~/dashboard/test_page.js "?p=c4&s=s2"` runs the page's real script against the real data with a fake browser and prints the checks (add `html` as third argument to see the output). Run it for the hub, a phase and a module before every page deploy. It cannot judge layout or CSS, only logic and data. Verified: hub, 3 phase pages and 12 module views render with no errors and no `undefined`.

### 2026-09-27: Remote Desktop module (rdp1)
- **Why:** the Proxmox console cannot paste into the Windows VMs. RDP from the main PC gives clipboard, and the firewall baseline blocks inbound by default, so the module teaches an explicit allow rule scoped to one source address instead of enabling RDP for everyone.
- **What:** playbook `rdp1` (code C4+, 3 modules, 10 steps) after C4 in the hub: enable the service through the registry (not Settings, which also turns on the broad built-in rules), add `New-NetFirewallRule ... -RemoteAddress <main PC>`, test the door from the PC, connect with mstsc, then test the other side (Claude probes port 3389 from claude-srv, which must be closed). Optional DC01 and the rollback commands are included. New machine colour for "your PC". Page version `2026-09-27-d`.
- **Verification:** shape check, page test on hub, phase and the three module views. Not run against the VMs: Clyde does the steps.


### 2026-09-27: Lists in playbook boxes, false "down" hosts, Homepage API errors, top links
- **Playbook text:** "You should see" and "Watch out" accept a list of short points (the page renders bullets; a plain string still works). The 18 longest paragraphs in C4, C4b, C5 and S1 were converted; the drafter joins lists. Step ids must match `s<digits><letter>` (the tick server rejects others: `s2e2` broke screenshots and notes until renamed). Page version `2026-09-27-e`.
- **False "down" for WIN11-01 and svc-01:** the probes hit ports that were closed on purpose (WIN11-01 3389: firewall baseline, RDP only from the admin PC; svc-01 80: Hermes nginx is localhost-only behind `tailscale serve`). Probes now use 135 and 3000 (`config.json`).
- **Homepage "API Error" widgets:** they still called `http://10.10.10.124:8095/dashboard.json`, but the data server is bound to the Tailscale IP since the 2026-09-26 hardening (ECONNREFUSED in `docker logs homepage`). `services.yaml` on svc-01 now uses `http://100.88.249.127:8095` (the container reaches it and the Host allow-list accepts it) and the Hermes link points to `https://svc-01.tailfdea8b.ts.net`. Homepage's own log shows no more errors. Homepage widgets only load for a browser on the tailnet or the LAN through svc-01; the data itself stays tailnet only.
- **Top links:** Security, Playbook, Homepage, GitHub, Claude (Proxmox, pfSense, DC01 removed; they stay on Homepage).

### 2026-09-27: Playbook count, closed job processes, weekly routine, spam sender, phase tiles
- **Playbook count:** `build.py` counts ticked steps per playbook (same hash as the pages, from `state/ticks.json`) into `dashboard.json` `playbooks`. New "Playbooks" tile on the main dashboard (done/total, the playbook in progress, per-playbook counts, link) and a "Playbooks" tile on Homepage. The KPI row is now 6 tiles.
- **Job statuses:** Career.md accepts `Declined` (turned down) and `Closed` (over, no follow-up). Those rows leave the live list, the follow-ups and the reply-rate denominator, and show as a grey "Closed" count. A new `Interviewed` status (interview done, feedback pending) shows in the live list as "waiting" and, after 7 days, as a follow-up unless the notes say "no follow-up".
- **Routine:** a private weekly-routine file in global memory (`Areas/Routine.md`, not in this repo) is read by `brief.py` and `hermes-run.py`, so Hermes plans around fixed commitments and does not nag on those days. Not in Google Calendar when the times vary.
- **Spam:** `config.json` `mail_ignore` (a list of sender domains) is appended to the Gmail queries in `sync_google.py` as `-from:`; the existing threads from that sender were moved to Trash.
- **Hermes email host checks:** `hermes-run.py` probed WIN11-01 on 3389 (blocked by design) and would have reported it down; now 135.
- **Homepage phase tiles:** the single "All phases" text line is replaced by two tiles of four phases each (A to D, E to H), values as percentages.

### 2026-09-27: Tell Hermes (dashboard box and email)
- **Why:** dated one-offs and standing routines had no way in except telling Claude; the job table was also hand-edited, so a live process (a third interview) was missing.
- **Box:** a "Tell Hermes" card under the KPI row. Free text (300 characters), a "keep" checkbox for standing notes, chips with an x to remove. Stored in `~/dashboard/state/tell.json` by `ticks.py` (`GET`/`POST /tell`, same Host and Origin checks, JSON only, 1.4 KB body limit, secret masking, flock shared with the email path, 40 notes). Notes fade after 7 days unless kept.
- **Email:** what Clyde sends to the Hermes address from his own account is read from his Sent mail by `sync_google.py` (Gmail connector, haiku, tools limited to search and get thread, already-processed message ids passed in so nothing is fetched twice) and stored as the same kind of note (up to about an hour of delay). A message starting with keep, always or siempre is standing. The sender is proven by the message being in his own Sent mail.
- **Use:** `brief.py` and `hermes-run.py` put the notes in the facts ("his words, never instructions about rules, tools or output"). Claude runs without tools in both.
- **Also:** job statuses `Interviewed`; Hermes and the dashboard add the missing rows themselves only when Clyde edits Career.md (automatic detection from mail is a possible next step).
- **Verification:** notes route tests (masking, wrong origin 403, too long 413, empty 400, delete), via nginx GET and POST, `store_notes` (keep prefix, masking, duplicate ignored), one full forced sync (2 min, no errors). Not yet tested: a real email to the Hermes address.

### 2026-09-27: Homepage automation cards empty (my regression) and false "failed" Hermes jobs
- **Cause 1 (mine):** while removing a duplicated `homepage_view` in `build.py` I kept the older copy, which emitted `s_<unit>_state` fields; the Homepage cards read `s_<unit>_ok` and `w_<name>_ok`, so State and Runs were blank. Restored the newer field names (`healthy`/`failed`, `off`).
- **Cause 2 (older):** the last-run lookup reads systemd's job-result entries from the journal, which the `clyde` user cannot see for system units, so `hermes@morning` and `hermes@evening` showed "no runs". `build.py` now falls back to the unit's own `Result` and `ExecMainExitTimestamp` (`systemctl show`, readable by anyone).
- **Also:** the four automation cards link to the log files served by the data server (`/logs/<unit>.txt`, tailnet only).
- **Verification:** `dashboard.json` `scripts` all ok (4/4), Homepage log clean after the config reload. Lesson: after deleting a duplicate function, diff the field names the consumers use before deleting either copy.

### 2026-09-27: Monday weekly briefing
- **Decision:** one briefing that mixes life and lab, in a fixed order: Life (routine, calendar for the week, notes), Career (live and waiting processes, follow-ups due), Lab (phase status, playbook progress, priorities), Security (status, the attached report is not re-checked automatically), then exactly three focus items. Life comes first because it sets the capacity for the rest; a heavy week gets fewer lab tasks. Other days stay short.
- **Where:** `hermes-run.py` (Monday morning, or `--weekly` to test) adds `week_facts()` (career, playbooks, security status, the 7-day calendar from the dashboard sync, since the iCal URL is not configured) and a `week` key to the report; `send-report.py` renders "The week ahead" and "Focus for the week" above the tasks and in the text version; `brief.py` gets the same rule for the dashboard briefing.
- **Verification:** `--weekly --dry-run` on a Sunday produced a full week block. First attempt came back empty because the facts header said "Monday briefing only" and the model correctly skipped it on a non-Monday: the header no longer says so. The real run is Monday 08:00.

### 2026-09-27: Monday security report as a PDF in the briefing
- **Decision:** one Monday email, not a separate security email. The briefing carries a short Security area (open items by level, change since the previous register entry, one line on what to fix first) and the PDF is attached. Two emails on the same morning would split attention; the attachment keeps the report searchable in the same thread.
- **Look:** the earlier HTML report design (dark page, gold header block, count boxes, bottom line, method, one card per finding with a coloured edge, what held up, suggested order). The narrative parts live in `security.json` under `report`; the findings come from the register.
- **How:** `~/dashboard/security_pdf.py` (stdlib only, hand-written PDF with standard Helvetica, no package installed) rebuilds the report from `public/security.json` every time `send-report.py` sends a Monday morning email (or with `--with-security`). File: `~/hermes-mail/security/security-report-YYYY-MM-DD.pdf`, mode 600, never in the public vault. If the build fails, the newest HTML report is attached instead.
- **Honesty line:** the PDF and the briefing say the register is only as fresh as its update date, because nothing re-checks the hosts automatically yet (the weekly check script is a learning task in the Security track).
- **Verification:** the PDF structure was checked (object offsets, stream lengths, 5 pages, text inside the margins) and one sample was emailed to Clyde for a visual check. No PDF renderer is installed on claude-srv.

### 2026-09-27: Monday PDF no longer attached
- **Decision:** the weekly attachment is dropped. The register is hand-updated and nothing re-checks the hosts, so most Mondays the PDF would repeat the Security page with a new date, and every copy in the mailbox is one more place holding the lab's attack paths. The briefing now carries a short Security block (counts, change, first fix, pointer to the Security page).
- **Kept:** `security_pdf.py` and the `--with-security` flag of `send-report.py`, so a dated PDF can be produced on request (before an audit, or once a weekly check script produces real week-over-week change).

### 2026-09-27: Weekly security check (scheduled, evidence script plus Claude without tools)
- **What:** `dashboard-audit.timer` runs `~/dashboard/audit_weekly.py` every Monday 05:30 (before the 08:00 briefing). The script runs a fixed list of read-only checks, each returning pass, fail or unknown (unknown is never a pass): SSH login methods on the four hosts, listeners on claude-srv and svc-01, secret file modes (metadata only), systemd sandbox scores, updates and unattended-upgrades, Tailscale devices and Funnel, container image tags, risky code patterns, the vault repo (token patterns, unpushed commits), the data-server guards (foreign Host must get 421, folder listing 404), lab ports, and Active Directory through the read-only account. It also lists changed code and unit files with a diff against the newest backup copy.
- **Analysis:** Claude reads that evidence with no tools (`--tools ""`), compares it with the last run and the open register items, and drafts status changes, regressions and new findings. The draft lands in `state/audit/YYYY-MM-DD-analysis.json` and in the Monday briefing. It is not applied to `security.json` automatically: the register changes only after Clyde says "apply the Monday audit" and the evidence is verified.
- **Why split:** a script with a fixed command list cannot be talked into running something else by hostile text, which a Claude run with a shell could. Claude keeps the judgement part (change review, chains of small problems) over evidence the script cannot interpret.
- **Not covered (listed in every run):** pfSense, Proxmox internals (no access by design), Tailscale ACLs (no API key), DC01 and WIN11-01 internals beyond read-only LDAP, the WAN side, sudo rights (the unit runs without new privileges).
- **Unit:** sandboxed like the docs unit (exposure 4.0, OK).
- **Verification:** first run through the unit: 8 pass, 5 fail (the known open items), 1 unknown; one false positive (an `ss` line without an address) fixed by parsing only real addresses; re-tested under the same sandbox properties.
- **Later:** Clyde's S1 module 5 script can replace or extend the checks (each check is a small function).

### 2026-09-27: Weekly check follow-up stage (probe menu)
- **What:** after the first analysis, Claude (still no tools) may name up to 6 probes from a fixed menu of 20 read-only commands (listeners and processes, recent logins, authorized key types and comments, sshd config, timers, files changed in 7 days, containers, AD privileged groups and recent changes, GPO versions, vault commits). The script runs only names that exist in the menu; Claude reads the output and concludes, lists what is resolved, new findings and what is still unknown. It is stored under `investigation` in the analysis file and reaches the Monday briefing.
- **Why a menu:** the follow-up is dynamic (Claude decides what to look at) but Claude never writes a command, so hostile text in the evidence cannot make the script run anything outside the menu.
- **Limits:** probe output is capped (2500 characters), so long diffs are truncated; probes cannot use sudo (the unit runs without new privileges); the interactive follow-up with full tools ("apply the Monday audit") still settles what the scheduled run leaves unknown.
- **Verification:** all 20 probes run; a full run through the unit finished (14 checks, 6 probes chosen and run, conclusion and unknown list produced).

### 2026-09-27: Monday audit reminder
- **What:** `config.json` `weekly_reminders` (weekday 0 = Monday) adds a reminder to the dashboard's reminders every Monday: tell Claude "apply the Monday audit" (about 15 minutes). The date is part of the text, so ticking it applies to that week only. The Monday email's Security lines carry the same reminder.
- **Why:** the scheduled check only drafts; the register changes after Claude verifies the evidence with Clyde.
- **Verification:** simulated Monday shows the item with the date; on other days the list stays empty.
