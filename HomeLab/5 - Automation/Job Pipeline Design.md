# Job Pipeline Design

Semi-automatic job search pipeline: collects offers, filters and ranks them, drafts
applications, and sends a daily digest. Clyde reviews and sends each application.
This is the `jobs-tracker` item from the butler roadmap. Python backend work, written by
Clyde (design and review support only from Claude).

## Current State

**Status:** ⬜ Design only. No code written.

### Why semi-automatic

Full auto-apply is rejected. LinkedIn, Glassdoor and InfoJobs prohibit bots in their terms,
generic applications get few replies, and a wrong auto-send stays in the application
history. The pipeline automates search, filtering, scoring and drafting. Sending stays manual.

### Sources

| Source | Method | Notes |
|---|---|---|
| LinkedIn | Job alert emails to Gmail | No public job API, scraping is against ToS and hits login walls |
| Glassdoor | Job alert emails to Gmail | Public API retired 2022, enterprise-only now, ToS bans scrapers |
| InfoJobs | Official API (`GET /offer`, `GET /offer/{id}`) plus alert emails | Register app at developer.infojobs.net, Client ID and Secret, HTTP Basic for app-level calls |
| Adzuna | Official API, country `es` | Free key, instant signup, limits 25/min, 250/day, 1000/week |
| Indeed | Job alert emails to Gmail | Same method as LinkedIn |
| Others (to check) | Jooble API, Tecnoempleo alerts, Welcome to the Jungle | Verify access method before adding |

Technojob excluded (Clyde's choice).

### Pipeline

```
Gmail alerts ─┐
InfoJobs API ─┼─> ingest -> normalize -> dedupe -> filter -> score -> draft -> digest
Adzuna API ───┘                              │                          │
                                             └──── SQLite tracker <─────┘
```

1. **Ingest.** Alert emails read through the Gmail API with read-only scope, one label for
   job alerts. API sources pulled once a day.
2. **Normalize.** One record per offer: source, url, title, company, location, salary
   (if given), description, date seen.
3. **Dedupe.** Same offer arrives from several sources. Key on normalized company, title
   and location, plus url.
4. **Filter.** Hard rules first: commute limit, excluded roles (sales, field-only
   hardware with mandatory driving licence), language requirements, minimum salary.
5. **Score.** Match against Clyde's CV and target track (sysadmin, Microsoft/AD, SOC).
   Keyword score first, optional small-model ranking later.
6. **Draft.** Short cover note per top offer, saved as a draft for review. Never sent
   automatically.
7. **Track.** SQLite table with state: `new`, `shortlisted`, `applied`, `interview`,
   `rejected`, `ignored`, plus date and next step.

### Delivery

Daily email digest at 07:00, readable on the commute (about 1h19 each way by public
transport). Top 10 ranked offers: title, company, score, commute estimate, link, draft
status. Sent through the existing Hermes mail path, no new sender.

A weekly summary (applied, interviews, response rate) is a later addition.

### Constraints

- No credential reuse from Claude Code files. The Gmail API needs its own OAuth client,
  read-only scope.
- Respect API rate limits (Adzuna 250/day). One daily run is enough.
- Offer data stays local (claude-srv). No offer or CV data in the public repo.
- Host: claude-srv (A8, always-on). No GPU needed for v1.

### Build order (Clyde writes, Claude explains and reviews)

1. SQLite schema and the normalized offer record.
2. InfoJobs and Adzuna clients (simplest, official APIs).
3. Gmail alert parser (one source at a time: LinkedIn, then Glassdoor, then Indeed).
4. Dedupe and hard filters.
5. Scoring.
6. Daily digest email on a systemd timer.
7. Draft generation.
8. Optional: wrap the tracker as an MCP server for the butler.

### Open decisions

- Commute limit and target zone (needs Clyde's home station).
- Minimum salary and contract types accepted.
- CV language(s) for drafts: Spanish, English, or both.
- Whether the digest also goes to a phone notification.

## Change Log

| Date | Change |
|---|---|
| 2026-10-03 | Design written. Source access checked: InfoJobs API (official, key required), Adzuna API (free, Spain supported), Glassdoor and LinkedIn (no usable public API, alerts by email instead). |
