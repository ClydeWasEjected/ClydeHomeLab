# Incident Response

Related: [[Security Process]] · [[Incidents Log]] · [[Hermes Dashboard]] · [[Homelab - Inventory]]

Status: **temporary draft v0, 2026-09-27.** Written by Claude so a plan exists today. It will be redone with Clyde as a lesson (tabletop exercise, real numbers, real contacts). Nothing here has been tested yet.

This repository is public. This document holds the process only: no addresses of weak spots, no keys, no passwords.

## Current State

### Roles

| Role | Who |
|---|---|
| Incident owner (decides, acts) | Clyde |
| Second pair of eyes (investigates read-only, keeps the timeline, writes the review) | Claude |
| Record | [[Incidents Log]] (narrative) and the Security page (open items) |

### What counts as an incident

Anything that may mean someone or something other than Clyde has access, or data was exposed, or a system stopped and the cause is unknown. A failed test or a bug is not an incident. When in doubt, treat it as one for the first 15 minutes.

### Severity

| Level | Meaning | Examples | Start acting within |
|---|---|---|---|
| SEV1 | Confirmed compromise or exposure of secrets or admin access | A key or token is public. Unknown logins on a server. Ransomware on a VM | Now |
| SEV2 | Probable compromise, or a critical service is down | Unexpected admin group change. A host behaves strangely. The firewall is down | 1 hour |
| SEV3 | Suspicious, no evidence of impact | A failed-login burst. A new unknown device on the network | 24 hours |

### The six steps

1. **Detect and record.** Write the time and what was seen. Keep the first note untouched.
2. **Triage.** Pick a severity. Decide what is affected and what could be reached from there.
3. **Contain.** Stop the spread first, without destroying evidence. Isolate, do not wipe.
4. **Eradicate.** Remove the cause: rotate secrets, remove keys and accounts, rebuild from a known good state.
5. **Recover.** Bring services back, one at a time, and check each one.
6. **Review.** Blameless write-up within 3 days: timeline, root cause, what worked, what changes.

### The first 15 minutes

- Write down the time and the symptom.
- Do not reboot, wipe or "clean up" yet. Memory and logs are evidence.
- Take a snapshot of the affected VM or container if it can be reached (Proxmox snapshot).
- Cut the network of the affected machine (unplug its virtual network card in Proxmox, or disable its firewall rule) instead of powering off, unless it is destroying data.
- Rotate the secret that may be exposed, before investigating.
- Tell Claude: "incident, severity ?, what I saw". Claude starts a timeline and investigates read-only.

### Evidence

Keep logs before they rotate: copy the relevant part of the system journal, the firewall log and the Active Directory event logs into a dated folder outside the affected machine. Screenshots are fine as long as they show no secret. Never paste a live secret into a chat: rotate it and say so.

## Runbooks

Each runbook is a short checklist. Steps are the ones to do first, in order.

### 1. A secret leaked (password, token, key, app password)

1. Rotate or revoke it at the source (the provider, the account, the host that trusts the key).
2. Put the new value only where it belongs (the server file with restricted permissions), never in chat or git.
3. Search for uses: config files, scripts, git history. If it reached the public repository, rotating comes first, rewriting history second (history rewrites do not undo what was already copied).
4. Check the provider's activity log for use between the leak and the rotation.
5. Record it: what leaked, how, how long, what it could reach.

### 2. Suspected compromise of a server (claude-srv or svc-01)

1. Isolate it from the LAN (Proxmox network device down), keep Tailscale access only if it is needed to investigate.
2. Snapshot it.
3. Revoke every credential the host holds: SSH keys it uses to reach other hosts, API tokens, mail passwords. Remove those trusts on the other side.
4. Check the other hosts it can reach for unknown logins and new files.
5. Rebuild from a known good state, restore data from backup, re-issue credentials. Do not reuse a suspect disk.

### 3. Suspicious behaviour on a Windows machine (WIN11-01, DC01)

1. Isolate it (Proxmox network device down). Do not shut it down.
2. Snapshot it, including memory if possible.
3. On the domain controller: list recent changes to privileged groups, new accounts, password resets, and GPO changes.
4. Reset the passwords of any account that logged on to the machine. For the domain, plan for the krbtgt account being reset twice if a domain controller is suspected.
5. Revert or rebuild the machine from a clean snapshot.

### 4. An Active Directory account is misused or locked out repeatedly

1. Disable the account, then check where the failed or unusual logons came from (source machine).
2. Check group membership changes and the last password change.
3. Reset the password, re-enable, and watch for a repeat.
4. If a privileged account is involved, treat as SEV1 and use runbook 3.

### 5. A Tailscale device is lost, stolen or unknown

1. In the admin console, remove the device and expire its keys.
2. Check the list of devices for anything unfamiliar.
3. Revoke any long-lived credentials that device held (SSH keys, tokens, saved passwords).

### 6. Data or service loss (disk failure, deleted VM, bad change)

1. Stop changing things. Note what was lost and when.
2. Restore from the newest good backup or snapshot. If there is none, say so in the review: that is a finding.
3. Verify the restore works end to end before declaring recovery.

### 7. A bad change broke something

1. Roll back using the plan written before the change.
2. Record the cause in [[Incidents Log]] and correct the change procedure.

## Post-incident review (template)

Copy into [[Incidents Log]] as a new section, newest on top.

- **Summary:** one paragraph, plain words.
- **Timeline:** time and event, from first sign to recovery.
- **Impact:** what was affected, what data or access was at risk.
- **Root cause:** why it was possible, not who did it.
- **What worked / what did not.**
- **Actions:** each with an owner and a date, tracked as tasks. Fixes become checks in the weekly security check.

## Open points for the lesson

- Real contact and escalation list (none needed for a lab, but decide who is told, if anyone).
- Backups do not exist yet, so runbooks 2, 3 and 6 rely on snapshots only. Fixing that comes first.
- Decide the log retention and where the evidence folder lives.
- Run one tabletop exercise per runbook and correct the steps that were unclear.
- Decide how alerts reach Clyde once monitoring exists (phase F).

## Change Log

### 2026-09-27: Temporary draft v0
- Written by Claude as a starting point: roles, severities, six steps, first 15 minutes, seven runbooks, review template. To be reworked together as a lesson. Not tested.
