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
| Secret | `~/hermes-mail/.env` → `EMAIL_PASSWORD=` (Gmail App Password, `chmod 600`) |

### Files

| File | What it is |
|---|---|
| `hermes-run.py` | Gathers facts, runs `claude -p --tools ""`, saves `report.json` + `history/`, calls the renderer |
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

## Change Log

### 2026-09-24: Built

- Researched Hermes Agent (Nous Research). Not used: no Claude Pro support, and the install was blocked in the Claude session. Built the same idea on Claude Code instead, see [[Hermes Design]].
- First email: static text report (05:20). Then redesigned as HTML following the StudentBoard Hermes email structure.
- Gmail iOS dark mode inverted white text on the dark header (date unreadable). Fixed by using light cards only, which Gmail inverts consistently. Checklist split into one card per group with larger boxes and spacing. Switched everything to English.
- Added book lessons: 8 books, 16 lessons, excerpts only where the wording is known to be accurate.
- Automated: `hermes-run.py` with `claude -p --tools ""`, morning and evening timers.
- **Verification:** dry runs of both modes produced valid reports from live data (about 1 minute each). The morning run correctly flagged DC01 on the A8 as urgent and WIN11-01 as not answering on 3389.
- **Open:** the App Password in `.env` was pasted in a chat. Rotate it.
