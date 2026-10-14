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

### Roadmap (ordered, proposal 2026-10-14)

Decision: mixed, three lanes (Microsoft admin bridge, SOC, red team). Red team is the goal, SOC is a tool, not the destination. Lab work already in the Hermes playbook (pfSense A, VLAN B, AD C incl. C7 vulnerable AD, monitoring F, offensive lab G, red team scenario and pentest report H, identity E) is not repeated here. This doc only covers certs and study that sit outside the playbook.

#### Free (now, evenings after Adecco)

| Order | Item | Where it lives |
|---|---|---|
| 1 | Playbook A and B (pfSense, VLANs), the base for everything | Playbook |
| 2 | TryHackMe beginner paths and HTB Academy Tier 0, 30 to 60 min a day, in parallel the whole time | Not in playbook |
| 3 | SC-300 study (identity), with Entra and Intune at Adecco | Playbook track E |
| 4 | SC-900 if the free Microsoft voucher is still offered (verify) | Not in playbook |
| 5 | Playbook F (Sysmon, central collection, SIEM, detection rules) | Playbook |
| 6 | SC-200 Microsoft Learn path, plus one Sentinel (free tier) and one Splunk lab | Not in playbook (F is a generic SIEM) |
| 7 | Playbook C7, G and H (vulnerable AD, attacks, detection, scenario, pentest report) | Playbook |

#### Paid (from 2027, budget permitting)

| Order | Cert | Approx cost | Condition |
|---|---|---|---|
| 1 | SC-300 | about 165 USD (verify) | Already studied for free, pay the exam only. Bridge job lane. |
| 2 | HTB CPTS | about 490 USD (Academy plus voucher) | After playbook G and H are done. Best value for red team. No European hiring data found. |
| 3 | PNPT (399 to 499 USD) or OSCP (1,499 to 1,749 USD) | | PNPT for an affordable AD-focused cert. OSCP only if target postings name it. |
| Optional | SC-200 (about 165 USD, verify) or HTB CJCA (about 175 USD) | | Only if a SOC role becomes the target. |
| Optional | Security+ (about 439 USD, 404 in older sources) or CySA+ | | Only if postings ask for it. |
| Later | CRTO | not checked | When the AD lab is mature. |

Rejected: CCST and Linux Essentials (low signal for someone with IT support experience, exam not free), SC-900 and AZ-900 as paid exams, AZ-104 and MD-102 unless a posting names them.

Move-on rule: pay for CPTS only after playbook G and H have produced written reports. Re-check in 2027 with 10 to 15 real junior pentester and SOC L1 postings (LinkedIn, InfoJobs) to decide on SC-200, Security+ and OSCP.

Evidence behind the lanes (2026-10-14, job-board snippets and blogs, no verified counts): Barcelona M365/Azure admin postings (Michael Page 27,000 to 33,000 EUR, Nextret 36,000 to 42,000 EUR) ask for hands-on Entra, Intune and PowerShell and rarely name certs. Spanish SOC L1 listings ask for SIEM experience (Splunk, QRadar, Sentinel, ArcSight), Linux and cloud, certs are a plus. Guides say entry-level security headcount shrank and the common route is admin or cloud, then SOC or pentest, then offensive certs. Red team prices from vendor-affiliated comparison sites. L1 SOC pay 22,000 to 30,000 EUR is a weak source.

## Open Questions

- Balance: this research only searched cybersecurity, so it is cyber-heavy by construction. Demand for sysadmin/Microsoft admin roles in Barcelona (MD-102, AZ-104, SC-300 as hiring bridge) was not researched. Junior SOC listings seen ask for experience, so the security target likely needs an IT/cloud-admin bridge job first.
- Budget and date for 2027 certs.
- Whether to replace the order in `CLAUDE.md` and the Hermes cert tracks with the roadmap above.
- Whether to add the "not in playbook" items (THM/HTB Tier 0, SC-900 voucher, SC-200 path plus Sentinel/Splunk labs) to the Hermes playbook as new modules. Playbook is frozen, waiting for Clyde's yes.
- Verify before buying: ISC2 CC free terms, SC-900 voucher, HTB pricing, CJCA price, exam prices for SC-200/SC-300 in EUR.

## Change Log

- 2026-10-14: Merged the red team table, mixed review and ordered free/paid roadmap into one "Roadmap" section. Removed write-ups, attacking AD and monitoring from the free list (already in playbook F, G, H, C7).
- 2026-10-14: Added all-cyber vs mixed review (Barcelona admin postings, Spanish SOC L1 requirements). Decision proposed: mixed, three lanes (bridge, SOC, red team).
- 2026-10-14: Added red team leaning section. CCST and Linux Essentials rejected (low signal, exam not free). Replaced with eJPT, CPTS, PNPT, OSCP, CRTO.
- 2026-10-04: ISC2 CC marked unavailable (voucher expired). Added balance question.
- 2026-10-04: Created. 5 research topics (SOC certs, pentest certs, free certs, whether certs matter, Spain market), sources graded above.
