# Hermes

Related: [[Hermes Design]] · [[claude-srv]]

## Current State

| Item | Value |
|---|---|
| Host | `claude-srv` (CT 105), user `clyde` |
| Location | `~/hermes-mail/` |
| From / To | Hermes sender account → personal inbox (addresses in `send-report.py` on claude-srv, kept out of the public repo) |
| Schedule | `hermes-morning.timer` 08:00, `hermes-evening.timer` 22:00 (Europe/Madrid) |
| Service | `hermes@.service` (template: `hermes@morning`, `hermes@evening`), `TimeoutStartSec=900` |
| Secret | `~/hermes-mail/.env` (`chmod 600`) → `EMAIL_PASSWORD=` (App Password of the Hermes bot account, for sending) |
| Inbox source (morning) | `.env` → `GMAIL_USER=<main Gmail>`, `GMAIL_IMAP_PASSWORD=` (App Password of that account). IMAP, `readonly`, headers only |
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


### 2026-09-25: Weekly security report attachment
- **Changed:** `send-report.py` attaches the newest `~/hermes-mail/security/security-report-*.html` to the **Monday morning** email only; the subject gets "weekly security report (date)". `--with-security` forces it on other days. Backup: `send-report.py.bak-20260925c`.
- **Why:** a weekly security view without a separate email. The reports are **deliberately not in this repo**: the repo is public and a security report maps attack paths. `security/` is mode 700.
- **Verification:** `py_compile` OK; the first report (2026-09-25) was sent through the same `send()` path with the attachment; Gmail SMTP accepted it (arrival to be confirmed by Clyde).
- **Open:** nothing regenerates the report yet, so Mondays re-send the newest one (its date is in the subject). An automated weekly check script is a pending learning task.

### 2026-09-25: Light and dark mode
- **Problem:** the first luxury-theme send (08:01) arrived light on Gmail iOS. Gmail iOS fully inverts HTML mail in dark mode and ignores `color-scheme`, so the black palette flipped to cream.
- **Changed:** `send-report.py` now has `LIGHT` and `DARK` palettes. Inline styles use the champagne/gold light palette (Gmail inverts it to a dark look by itself). `dark_css()` adds a `prefers-color-scheme: dark` block for Apple Mail and Outlook that maps every inline light colour (background, text, borders) to its black/champagne/gold equivalent through attribute selectors, so the markup needs no classes. Meta `color-scheme` is now `light dark`. Urgent card colours moved into the palette. Backup: `send-report.py.bak-20260925d`.
- **Verification:** `py_compile` OK; `preview.html` rendered with the light palette plus the dark override block; `lessons_sent.json` unchanged. One test email ("[TEST light/dark]") sent to the personal inbox; appearance on Gmail iOS light and dark to be confirmed by Clyde.

### 2026-09-25: Black and gold in the Gmail app
- **Changed:** `send-report.py` `lock_backgrounds()` repeats every background as a one-colour gradient in its dark twin (base `#000000`, cards `#0d0b08`). Text keeps the light palette. Backup: `send-report.py.bak-20260925d`.
- **Why:** the Gmail app's dark mode rewrites email colours, which turned the design brown-grey. It leaves background images alone, and it turns the light palette's dark text into ivory and gold.
- **Verification:** five test emails on the iPhone Gmail app (A to E); "D" chosen by Clyde. The full report preview was sent the same day.
- **Open:** check one email on the laptop. A client that doesn't auto-darken may show dark text on black; the fallback is test "E" (real colours inline, Gmail-only colour flip).

### 2026-09-26: Detailed lesson of the day
- **Changed:** every entry in `lessons.json` gained `from_book` (a story from the book, only where it's a known example, otherwise empty), `in_practice` (the idea applied to Clyde's week), `apply` (two concrete steps) and `question`. `send-report.py` shows them in the morning **and** evening emails (the excerpt and key points were morning-only before), and in the plain-text version. Backups: `lessons.json.bak-20260926`, `send-report.py.bak-20260926`.
- **Why:** Clyde asked for more depth. The detail is written once into the file, so sending costs no extra Claude call (the 2026-09-25 evening run had already failed on a usage limit).
- **Verification:** rendered with two lessons (with and without a story); a preview of last night's recap was sent.
- **Also 2026-09-25:** the evening run failed at 22:00 on a Claude usage limit (reset 22:30). It was re-run by hand at 23:59 and sent. Open: add a retry (systemd `Restart=on-failure` with a delay, or wait for the reset time), a pending task for Clyde.

### 2026-09-27: Evening recap lost to a DNS blip; SMTP send now retries

- **Symptom:** the Sunday evening recap never arrived. No failure email either, so it was a silent miss.
- **Root cause:** `hermes@evening.service` fired on time (22:00 CEST) but `ask_claude()` failed with `socket.gaierror`/`EAI_AGAIN` (couldn't resolve `api.anthropic.com`). `main()` correctly fell back to `send-report.py --error`, but that call hit the *same* transient DNS window and failed resolving `smtp.gmail.com`, so the failure notification also silently died. DNS on `claude-srv` (via `10.10.10.1`) resolved normally seconds later when checked by hand; treated as a one-off blip, not a persistent resolver problem (nothing else in the lab shows DNS issues around that time).
- **Fix (SMTP layer):** `send-report.py`'s `send()` now retries the SMTP connection up to 3 times (10s apart) on `socket.gaierror` / `OSError` / `smtplib.SMTPException`, covering both normal report sends and `--error` notifications. If all retries still fail, it appends the failure to `~/hermes-mail/send-failures.log` before re-raising, so a total outage stays discoverable on the host even with no email at all.
- **Fix (source layer, same evening):** `ask_claude()`'s failure was the actual gap the SMTP retry doesn't reach, since it's a different call (the Claude CLI, not SMTP). `hermes-run.py` gained `is_network_error()`, matching `gaierror` / `EAI_AGAIN` / "Temporary failure in name resolution" / connection refused-unreachable, mirrored on the existing `is_usage_limit()` pattern. On a network failure (and not already a retry), the run now reschedules itself once via `systemd-run --on-active=300s` (`NETWORK_RETRY_DELAY`), the same one-shot mechanism the usage-limit path already used, instead of going straight to an error email. Capped at one retry per run like the usage-limit path, so a real outage still ends in an error email rather than looping.
- **Verification:** `py_compile` OK on both files. SMTP retry exercised with a mocked client: recovers after 2 simulated `gaierror`s, sends on the 3rd attempt; permanent failure still raises and writes the fallback log line. `is_network_error()` checked against the actual Sunday error string (matches) and against a usage-limit string (does not, no overlap with `is_usage_limit()`). The missed Sunday evening recap was sent by hand once DNS was confirmed working (`hermes-run.py evening`, 23:33 CEST, `history/2026-09-27-evening.json`); the new reschedule path has not yet fired for a real blip.
- **Follow-up:** none open.

### 2026-09-26: Mailer verifies Gmail's certificate
- **Found (audit):** Python's default TLS context for `smtplib.starttls()` and `imaplib.IMAP4_SSL` does not verify certificates, so the app password was sent to whoever answered on the LAN path to Gmail.
- **Changed:** `send-report.py`, `hermes-run.py` and `gf/send-gf.py` pass `ssl.create_default_context()`. Backups `*.bak-20260926-tls`. Rule for new mail code: always pass a verifying context.
- **Verification:** verified handshake to `smtp.gmail.com:587` and `imap.gmail.com:993` (no login in the test), the same context refuses a wrong hostname, and a real report email was sent through the fixed code.

