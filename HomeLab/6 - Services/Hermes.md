# Hermes

Related: [[Hermes Design]] · [[claude-srv]]

## Current State

| Item | Value |
|---|---|
| Host | `claude-srv` (CT 105), user `clyde` |
| Location | `~/hermes-mail/` |
| From / To | `hermes.studentboard@gmail.com` → `clyde.jcaiga@gmail.com` |
| Schedule | `hermes-morning.timer` 08:00, `hermes-evening.timer` 22:00 (Europe/Madrid) |
| Service | `hermes@.service` (template: `hermes@morning`, `hermes@evening`), `TimeoutStartSec=900` |
| Secret | `~/hermes-mail/.env` (`chmod 600`) → `EMAIL_PASSWORD=` (App Password of the Hermes bot account, for sending) |
| Inbox source (morning) | `.env` → `GMAIL_USER=clyde.john253@gmail.com`, `GMAIL_IMAP_PASSWORD=` (App Password of that account). IMAP, `readonly`, headers only |
| Calendar source (morning) | `.env` → `GCAL_ICS_URL=` (Google Calendar → Settings → calendar → "Secret address in iCal format") |

### Files

| File | What it is |
|---|---|
| `hermes-run.py` | Gathers facts (plus Gmail and Calendar in the morning), runs `claude -p --tools ""`, saves `report.json` + `history/`, calls the renderer |
| `send-report.py` | Renders `report.json` to HTML + plain text, picks the lesson, sends. `--error` sends a failure email |
| `lessons.json` | 16 lessons: quote, chapter, excerpt, key ideas, "for you today", mood tags |
| `lessons_sent.json` | Lessons already sent (no repeats until all are used) |
| `report.json` | Last generated report |
| `history/` | Every report, `YYYY-MM-DD-morning.json` / `-evening.json` |
| `preview.html` | Last rendered email |

### Operations

| Task | Command |
|---|---|
| Send a morning report now | `sudo systemctl start hermes@morning` |
| Preview without sending | `python3 ~/hermes-mail/hermes-run.py morning --dry-run` |
| See next runs | `systemctl list-timers 'hermes-*'` |
| Logs of the last run | `journalctl -u hermes@morning -n 50` |
| Change the time | edit `OnCalendar=` in `/etc/systemd/system/hermes-<mode>.timer`, then `sudo systemctl daemon-reload` |
| Rotate the App Password | new App Password in Google, replace it in `.env`, revoke the old one |
| Pause | `sudo systemctl disable --now hermes-morning.timer hermes-evening.timer` |
| Turn off inbox or calendar | remove `GMAIL_*` or `GCAL_ICS_URL` from `.env`; the card disappears |
| Rotate the calendar URL | Google Calendar → "Reset" next to the secret address, paste the new one in `.env` |

## Change Log

### 2026-09-24: Built

- Researched Hermes Agent (Nous Research). Not used: no Claude Pro support, and the install was blocked in the Claude session. Built the same idea on Claude Code instead, see [[Hermes Design]].
- First email: static text report (05:20). Then redesigned as HTML following the StudentBoard Hermes email structure.
- Gmail iOS dark mode inverted white text on the dark header (date unreadable). Fixed by using light cards only, which Gmail inverts consistently. Checklist split into one card per group with larger boxes and spacing. Switched everything to English.
- Added book lessons: 8 books, 16 lessons, excerpts only where the wording is known to be accurate.
- Automated: `hermes-run.py` with `claude -p --tools ""`, morning and evening timers.
- **Verification:** dry runs of both modes produced valid reports from live data (about 1 minute each). The morning run correctly flagged DC01 on the A8 as urgent and WIN11-01 as not answering on 3389.
- **Open:** the App Password in `.env` was pasted in a chat. Rotate it.

### 2026-09-25: Luxury theme

- `send-report.py` palette changed from light/purple to black, champagne and gold (shared with the Homepage Hermes panel). Serif (Georgia) for the date, stats, quote and signature. `color-scheme: dark` meta so mail clients don't force-invert it. Layout unchanged.
- Backup: `~/hermes-mail/send-report.py.bak-20260925`.
- **Verification:** `send-report.py` without `--send` rendered `preview.html` with the new palette; nothing sent, `lessons_sent.json` unchanged. First real send: next timer run.

### 2026-09-25: Inbox and calendar in the morning email

- Morning email gets two new cards after the tasks: **Calendar** (today and tomorrow) and **Inbox** (counts, "needs you", job-search news). Evening email unchanged.
- `hermes-run.py`: `inbox_facts()` reads Gmail over IMAP (`readonly`, `BODY.PEEK` of From/Subject/Date only, Gmail search via `X-GM-RAW`, uses the `Newsletter` and `Job Applications/*` labels). `calendar_facts()` parses the secret iCal feed with the standard library (no new packages). Each source is wrapped so a failure shows as "unavailable" instead of killing the report.
- Prompt: email and calendar lines are marked as untrusted data; the model still runs with no tools.
- `send-report.py`: renders the two cards and adds them to the plain-text version. All text escaped.
- Backups: `hermes-run.py.bak-20260925`, `send-report.py.bak-20260925b`.
- **Verification:** calendar parser tested on a sample feed (TZID, UTC, all-day, weekly `BYDAY` with `EXDATE`, expired `UNTIL`): correct Madrid times. Wrong IMAP login returns "unavailable", report continues. Renderer test: cards shown, HTML escaped, `lessons_sent.json` unchanged. Full `--dry-run` without credentials: `inbox`/`calendar` empty and cards hidden; test history file removed afterwards.
- **Open:** add `GMAIL_USER`, `GMAIL_IMAP_PASSWORD` and `GCAL_ICS_URL` to `.env` (typed on the server, not pasted in chat), then run `--dry-run` once to see real data.

