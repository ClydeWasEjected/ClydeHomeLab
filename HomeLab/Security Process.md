# Security Process

Related: [[Hermes Dashboard]] · [[Incidents Log]] · [[Incident Response]] · [[Homelab - Inventory]] · [[Homelab - Project Overview]]

Status: draft 2026-09-26. Proposed rules, Clyde confirms or changes the numbers (playbook S1, module 4).

## Current State

### Roles

| Role | Who |
|---|---|
| Owner (accepts risk) | Clyde |
| Administrator (makes the fixes) | Clyde |
| Independent verifier (audits, checks fixes live) | Claude |
| Record | Security page (tailnet only) and the audit report emailed by Hermes |

### Severity and deadlines

| Level | Meaning | Fix or decide within |
|---|---|---|
| Urgent | Exploitable now with real impact (admin access, data exposure), or a flaw in something we run that is actively exploited (CISA KEV list) | 7 days |
| Soon | Real weakness that needs a foothold or a mistake to use | 30 days |
| Later | Hardening, small exposure | 90 days |
| Watch | Risk with no action available, or a risk accepted on purpose | Reviewed monthly |

- Rating: impact 1 to 3 times likelihood 1 to 3. 1 to 2 Later, 3 to 4 Soon, 6 to 9 Urgent. Adjust for context and write the reason.
- Every finding has an owner, a level and a decision: fix, reduce or accept. An accepted finding has a written reason and a review date.
- Only a verified finding is closed: checked live by someone other than the person who fixed it.

### Routine

| When | What |
|---|---|
| Weekly (Monday, 30 min) | Read the Hermes security report and the Security page. Run the weekly check script. Check pending security updates on the Debian hosts. Look at failed logins in the SSH journal and at failed systemd units. Log three lines in the Change Log below |
| Monthly | Patch window (see below). Review tailnet devices and keys. Update the inventory. Review accepted exceptions |
| Quarterly | Full audit by Claude as a second pair of eyes. Review who has sudo, which SSH keys exist and what Claude is pre-approved to do |
| After an incident | Record it in [[Incidents Log]] (what, root cause, fix, verification), then ask whether this routine would have caught it |

### Patching rules

| Component | Source | Method | Cadence |
|---|---|---|---|
| Debian hosts (claude-srv, svc-01) | apt | Security updates automatic (unattended-upgrades). Everything else and reboots in the monthly window | Security daily, rest monthly |
| Proxmox nodes | Proxmox repositories | `apt dist-upgrade` or the GUI, in a window, with a backup or snapshot first | Monthly |
| pfSense | Netgate | System, Update, after a config backup | Monthly |
| Windows lab VMs | Windows Update | After Patch Tuesday, snapshot first | Monthly |
| Container images | Registry | Pull and recreate, tags pinned | Monthly |

The severity deadlines apply to patches too: a patch for a flaw that is being exploited is done within 7 days, outside the window.

### Change control for fixes

1. Back up or snapshot first.
2. One change at a time.
3. Run the check-only form first (`sshd -t`, `--dry-run`, `apt-get -s`).
4. Test the good path and the bad path (the thing that should now fail, fails).
5. Keep a way back and know the command.
6. Have it verified, then log it.

### Public repo rule

This repository is public. Documents record rules and what was fixed, never open weaknesses or attack paths. Audit reports and the register stay on the Security page (tailnet only) and in the Hermes email.

## Change Log

### 2026-09-26: Draft created
- **Why:** after two audits the routine lived only in Claude's memory. Clyde asked for a real process he can run without Claude.
- **What:** severity model with deadlines, weekly, monthly and quarterly routine, patching rules per component, change control, the public repo rule. Rules are proposed: confirm or change them in playbook S1 module 4.
- **Next:** weekly check script (playbook S1, module 5), first weekly review logged here.
