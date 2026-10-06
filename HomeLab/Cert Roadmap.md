# Cert Roadmap

Research-based cert plan for the SOC to red-team goal. Two paths: a paid path (starts when budget exists, 2027) and a free path (now). Research done 2026-10-04. Proposal only: it does not replace the cert order in `CLAUDE.md` until Clyde decides.

## Current State

### What the evidence says

| Question | Finding | Source quality |
|---|---|---|
| Do certs gate hiring? | Not mostly. ISC2 hiring-manager survey: 90% would consider IT experience alone, 89% would consider entry-level certs alone. Top valued skills are problem-solving, teamwork, analytical thinking. One postings analysis: ~75% of cyber postings name no cert, ~7% require one. | ISC2 pages opened (good). Postings stat from search snippet only, research.com blocked (unverified). |
| Which cert is the HR filter? | Security+ has the highest hard-requirement rate and the DoD 8570 mandate behind it. That is a US effect. | Aggregators, US-centric. |
| What do Barcelona SOC postings ask? | EY Barcelona SOC listing: CISM, CISSP, OSCP, CEH or GPEN, B1/B2 English, 3 years, Splunk SIEM. Many "junior" listings want more experience than junior. | One listing via search snippet. Small sample. |
| Pay | Levels.fyi Spain security analyst median 31,920 EUR (31 submissions), Barcelona 30,605 EUR. Glassdoor snippet: Barcelona SOC avg ~23,000 EUR, range 18,750 to 36,500. | Small samples, treat as rough. |
| Hands-on vs multiple choice | Hands-on certs (BTL1, CPTS, HTB CJCA, SAL1) are called hard to fake, but have less name recognition than CompTIA. | Mostly vendor or reviewer opinion. |
| Free certs | Only proctored ones carry weight. ISC2 CC is the one free cert with a real exam. Completion badges (Google, IBM, Cisco, Fortinet NSE 1 to 3) are weak. | Two comparison articles opened, consistent. |

### Source notes and bias

- **ISC2 early-career hiring research, ISC2 2025 Workforce Study, ISC2 CC page:** opened. Best sources here. Bias: ISC2 sells certs.
- **Levels.fyi Spain:** opened. Only 31 submissions.
- **EpicDetect (SOC certs ranked):** opened. Sells competing lab platform, so it pushes "certs open doors, labs get you through". Useful for BTL1 view, discount the rest.
- **StationX SOC certs:** opened. Sells training, covers only Security+, GISF, CySA+. Said nothing on BTL1, CJCA, SC-200.
- **Tiago Nunes (CPTS before OSCP) and CybersecurityElite CPTS review:** opened. Practitioner opinion. Both admit CPTS has little HR recognition yet and say nothing about Europe. CPTS exam is about 10 days, needs about 85% of flags plus a report, voucher around 490 USD.
- **Unihackers and CertSelect free-cert comparisons:** opened. Agree on which free certs are proctored.
- **HTB CJCA (HTB blog and reviews), BTL1 reviews, HTB/THM pricing pages, EY listing, Glassdoor, SalaryExpert:** search snippets only. Fetch was blocked or I did not open them. Treat as unverified.
- **Blocked or dead (403/404):** InfoSec Institute, Fennell OSCP vs CPTS, FusionCyber, research.com, Glassdoor, SalaryExpert.

### Judgment

1. Clyde already has the thing ISC2 says matters most: prior IT work experience. Certs are the second lever, not the first.
2. The strongest evidence for Security+ is US-specific. In Spain the senior-leaning listing seen asked for CEH/CISSP/OSCP-tier certs and Splunk. Security+ is cheap insurance, not the top priority. This corrects my earlier "worth adding after SC-300" suggestion: it is optional.
3. SC-900 and AZ-900 are low signal for a SOC/red-team target. They are cheap, but they are not what moves hiring. SC-900 can be free (below).
4. For SOC, SC-200 and a practical cert beat the fundamentals pair. HTB CJCA is the best-aligned practical cert (SOC plus pentest, 100% hands-on, 5 days) but is new (July 2025) so employer recognition is unproven. Its value is the study path and the skills, not the badge.
5. CPTS is the best-value red-team cert, but belongs after the monitoring phase, matching the vault rule (understand, attack, detect, fix).
6. Splunk showed up in Barcelona listings, Sentinel did not. Worth one Splunk lab beside Wazuh/Sentinel.

### Paid path (from 2027)

| Order | Cert | Approx cost | Why |
|---|---|---|---|
| 1 | HTB CJCA | 175 USD with path unlock | Practical, SOC and pentest, best signal per euro. Recognition unproven. |
| 2 | SC-200 | exam about 165 USD (verify) | Sentinel/KQL/Defender XDR. Feeds the security monitoring phase. |
| 3 | SC-300 | exam about 165 USD (verify) | Already built into Hermes track E. Identity attacks are the red-team angle. |
| 4 | Security+ (optional) | 404 USD | HR filter for MSSPs and consultancies that screen by it. Skip if postings do not ask. |
| 5 | HTB CPTS | about 490 USD voucher plus Academy subscription | Red-team phase. OSCP only if a target posting names it. |

Deferred: SC-900, AZ-900 (low signal), AZ-104, MD-102 (job-relevant to the Adecco role, not to the SOC goal; take only if the job needs it).

### Free path (now, evenings after Adecco)

| Tier | Item | Cost | Why |
|---|---|---|---|
| X | ISC2 Certified in Cybersecurity | voucher already redeemed and expired (Clyde, 2026-10-04) | Was the only free cert with a proctored, accredited exam. Unknown whether ISC2 support will reissue an expired voucher; worth one email, not worth planning around. |
| A | Microsoft Learn SC-200 learning path | free | Same content as the paid cert. Study now, pay for the exam in 2027. |
| A | Homelab write-ups (Wazuh, Sentinel free tier, Splunk) | free | Documentation and reporting are explicit entry-level expectations in ISC2 research. The vault is the portfolio. |
| A | TryHackMe free rooms | free, 1 hour/day AttackBox | Structured beginner paths. SAL1 (paid) is the SOC-recognised one later. |
| A | HTB Academy Tier 0 modules | free, 30 starter cubes | Fundamentals only. Pricing changes were reported for 12 Oct 2026, check the site. |
| B | SC-900 | free exam voucher via Microsoft Virtual Training Days (one source, verify) | Real proctored exam at no cost. Low signal, take only if the voucher is still offered. |
| B | LetsDefend (now owned by HTB) | check free tier | SOC simulation practice. Free tier not verified. |
| Skip | Google Cybersecurity Certificate, IBM Analyst, Cisco Intro, CISA Cyber Essentials, Fortinet NSE 1 to 3 | | Completion badges, no identity-verified exam. Redundant with Clyde's IT background. |

Offensive free content (HTB Tier 0, THM beginner rooms) is for fundamentals only. Main effort stays blue team and homelab until the monitoring phase exists.

## Open Questions

- Balance: this research only searched cybersecurity, so it is cyber-heavy by construction. Demand for sysadmin/Microsoft admin roles in Barcelona (MD-102, AZ-104, SC-300 as hiring bridge) was not researched. Junior SOC listings seen ask for experience, so the security target likely needs an IT/cloud-admin bridge job first.
- Budget and date for 2027 certs.
- Whether to replace the order in `CLAUDE.md` and the Hermes cert tracks with the paid path above.
- Verify before buying: ISC2 CC free terms, SC-900 voucher, HTB pricing, CJCA price, exam prices for SC-200/SC-300 in EUR.

## Change Log

- 2026-10-04: ISC2 CC marked unavailable (voucher expired). Added balance question.
- 2026-10-04: Created. 5 research topics (SOC certs, pentest certs, free certs, whether certs matter, Spain market), sources graded above.
