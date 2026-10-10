# Remote Desktop

Related: [[WIN11-01]] · [[AD Administration]] · [[Active Directory Design]]

RDP into the domain client so copy and paste work (the Proxmox console has no clipboard), with port 3389 opened deliberately and not through the broad built-in rules. Playbook module C4+ (`rdp1`). Separate from LAPS (module C4b): LAPS manages the local admin password, this doc covers how a session reaches the machine.

## Current State

| Item | Value |
|---|---|
| Target | `WIN11-01` (`10.10.10.22`). RDP on `DC01` is optional and not done |
| Service | `fDenyTSConnections = 0` (registry), `TermService` running |
| Door (design) | Inbound rule `RDP from admin PC`: TCP 3389, source `10.10.10.23` only |
| Built-in rule group "Remote Desktop" | Must stay disabled: it accepts any device on the network |
| NLA | On (client proves identity before a session starts) |
| Who may sign in | Local `Administrators` (includes `lapsadmin`), plus members of `SG_RDP_Access` |
| Group | `SG_RDP_Access`, `OU=Groups,OU=IT,OU=Departments`. Members (nested groups, 2026-10-04): `SG_Workstation_Joiners`, `SG_IT_Users`, `SG_IT_Admins` |
| GPO | `GP-RDP-Access`, linked to `OU=Departments`. Intent: Group Policy Preferences, Local Users and Groups, Update `Remote Desktop Users (built-in)` adding `JNCLYDEHL\SG_RDP_Access`; User Rights Assignment, Allow log on through Remote Desktop Services: `Remote Desktop Users`, `Administrators` |

**Sign-in formats**

| Account | Type this | Note |
|---|---|---|
| Domain user | `JNCLYDEHL\<user>` | Must be in `SG_RDP_Access` (or local Administrators) |
| LAPS account | `WIN11-01\lapsadmin` | Local account: without the `WIN11-01\` prefix Windows tries the domain and reports "incorrect". Password from `Get-LapsADPassword`, pasted |

**Design decisions**

- One explicit allow rule with a name, a port and a source address, instead of "allow any".
- Registry switch, not Settings > Remote Desktop: the Settings toggle also enables the built-in rules that accept any source.
- Access by a named group (`SG_RDP_Access`), not `Domain Users`: every account that can RDP is an attack path on a workstation.
- Group Policy Preferences with action Update, not Restricted Groups, for `Remote Desktop Users`, so existing members are not wiped on each refresh.

## Verification (open items)

- Probe `10.10.10.22:3389` from `claude-srv`: must be closed or filtered once the built-in rule group is disabled (playbook step s1c).
- `Get-NetFirewallRule -DisplayName "RDP*" | ft DisplayName,Enabled,Direction,Action`: only `RDP from admin PC`, Allow.
- `Get-NetFirewallRule -DisplayGroup "Remote Desktop" | select DisplayName,Enabled`: all disabled.
- `gpresult /r /scope computer` on `WIN11-01`: `GP-RDP-Access` listed; `Get-LocalGroupMember "Remote Desktop Users"` shows `JNCLYDEHL\SG_RDP_Access`.
- GPO contents not yet read back from SYSVOL (LDAP shows only that the GPO exists and where it is linked).

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "The connection was denied because the user account is not authorized for remote login" | Account is neither a local Administrator nor in `Remote Desktop Users`: `SG_RDP_Access` empty, or `GP-RDP-Access` not applied | Add the user to `SG_RDP_Access`, `gpupdate /force` on `WIN11-01`, check `Get-LocalGroupMember "Remote Desktop Users"`, retry |
| "Incorrect" for `lapsadmin` | Typed without `WIN11-01\`, or an old password (LAPS rotated it) | Use `WIN11-01\lapsadmin`, fetch a fresh password, paste it |
| `net user lapsadmin ...` error 8654 | Expected: Windows LAPS owns the account | Use `Reset-LapsPassword` instead |
| `Reset-LapsPassword`: "not running as a local administrator" | Window not elevated, or `adm.clyde` not yet local admin (`GPO-Local-Admins` not applied) | Run PowerShell as administrator, check `net localgroup administrators` |
| Connection times out | Source address not `10.10.10.23`, service off, or rule disabled | `Test-NetConnection 10.10.10.22 -Port 3389` from the PC, compare with the rule's `RemoteAddress` |

## Pending

Found 2026-10-10 while doing C5 step 6: RDP to `FS01` failed with "not authorized for remote login" because `GP-RDP-Access` is linked to `OU=Departments` only. `WIN11-01` is covered by inheritance (`OU=Computers,OU=Operations,OU=Departments`); `FS01` is in `OU=Servers` at the domain root, with no GPO linked.

- [ ] Link `GP-RDP-Access` to `OU=Servers` (then the manual `Add-LocalGroupMember "Remote Desktop Users" -Member "JNCLYDEHL\SG_RDP_Access"` on FS01 is no longer needed). The NetBIOS prefix is `JNCLYDEHL\`, not `AD\`.
- [ ] Run `redircmp` on DC01 so new joins land in a linkable OU instead of `CN=Computers` (decide: staging OU or `Workstations`).
- [ ] Create a `Workstations` / `Servers` OU split and link the GPO to each. Do not link at the domain root (it would reach the Domain Controllers).
- [ ] Put the enable-RDP setting and the scoped firewall rule in the GPO, so a new machine needs no manual step. The built-in "Remote Desktop" rule group stays off.
- [ ] Link `GPO-Local-Admins` to `OU=Servers` too, so `SG_IT_Admins` is a local Administrator on member servers (FS01 got it by hand in C5 step s1g). Do not link it to the Domain Controllers.
- [ ] Confirm the GPO applies on `WIN11-01` (`gpresult /r /scope computer`, events 1055 and 1006).
- [ ] Verify on a fresh test VM: `Get-LocalGroupMember "Remote Desktop Users"` shows `JNCLYDEHL\SG_RDP_Access`.

## Change Log

### 2026-10-04: Remote Desktop enabled, group-based access added

- **What changed:** RDP enabled on `WIN11-01` and used to sign in as `lapsadmin` with a pasted LAPS password (typing 20 symbols into the Proxmox console failed). `SG_RDP_Access` and `GP-RDP-Access` created, the GPO linked to `OU=Departments`.
- **Why:** Copy and paste into the VM, and a repeatable way to grant RDP by group instead of per machine.
- **Issue:** During troubleshooting the built-in "Remote Desktop" firewall rule group was enabled, which opens 3389 to any device on the network and contradicts the design. To be disabled; the scoped rule stays.
- **Issue:** `GP-RDP-Access` breaks the `GPO-` naming used by the other GPOs: rename.
- **Issue:** First test as a domain user returned "not authorized for remote login"; `SG_RDP_Access` had no members at that point. Fixed by nesting `SG_Workstation_Joiners`, `SG_IT_Users` and `SG_IT_Admins` into it.
- **Issue:** `gpupdate /force` on `WIN11-01` had been logging events 1055 and 1006 (computer policy). Not the cause here, but GPO delivery to this machine must be confirmed with `gpresult` before relying on `GP-RDP-Access`.
- **Verification:** `lapsadmin` signed in over RDP and copy/paste worked (reported by Clyde). The verification items above are still open.
