> [!NOTE] In plain words
> This page tells you how to run the deploy robot day to day: check that it works, fix it when it breaks, and change it safely. Why it is built this way: [[Automation Design]].

> [!TIP] Words used on this page
> - **Secret**: a password-like value that GitHub keeps hidden.
> - **Key pair**: two matching files. The public one is the lock, the private one is the key.
> - **Hash**: a short fingerprint of a file. Same hash means the files are identical.
> - **Rotate**: replace something with a fresh copy.
> - **Allowlist**: a list of approved names. Anything not on it is refused.
> - **Timer**: the schedule that runs a watchdog script every 60 seconds.

# Current State (as of 2026-09-22)

## What the robot needs

Nothing secret is stored in this repo.

| Name | What it is | Where it lives |
|---|---|---|
| `DEPLOY_SSH_KEY` | The key the robot uses to log into Proxmox | A GitHub secret. The original file is on your PC: `C:\Users\Clyde\.ssh\deploy-keys\homelab-ci-deploy` |
| `TS_OAUTH_CLIENT_ID` | The robot's ID for joining your Tailscale network | A GitHub secret |
| `TS_OAUTH_SECRET` | The password that goes with that ID. Shown once when created, never again. | A GitHub secret |

The lock that matches the deploy key sits on the host, with restrictions. Its fingerprint is `SHA256:OVcs3Lf6ZgdsgKNRV2573qRpfKMiv/xkD/4Y4w8esU4` (created 2026-09-18). A fingerprint is safe to share.

On Tailscale, the robot has a label (`tag:ci-deploy`) that lets it reach Proxmox on port 22 and nothing else. The name of its OAuth client is `github-actions-homelab-deploy`.

## Things you do often

### Deploy by hand
**When:** you want to push a script now, without waiting for GitHub. It uses the same path the robot uses.

```
bash "HomeLab/5 - Automation/scripts/deploy.sh" <script-name> <unit-name>
```

Example: `deploy.sh fix-orphan-taps.sh fix-orphan-taps`
### Check that the host has the same scripts as the repo
**When:** after a deploy, or any time you are unsure.

```
sha256sum "HomeLab/5 - Automation/scripts/"fix-*.sh
ssh root@100.121.216.124 "sha256sum /usr/local/bin/fix-*.sh"
```

The first command shows the fingerprints of the scripts in the repo. The second shows the ones on the host. **If the fingerprints match, the files are identical.**
### Check that the watchdogs are running
**When:** you want to know the scripts are alive.

```
ssh root@100.121.216.124 "systemctl list-timers 'fix-*' --no-pager"
ssh root@100.121.216.124 "journalctl -u fix-orphan-taps.service -n 3 --no-pager"
```

The first shows that the timers are scheduled. The second shows what the last runs printed.

## Things you do sometimes
Each one says **when** to do it and **why** the steps are in that order.
### Replace the deploy key (rotate it)

**When:** you think the key might have leaked, or once a year to be safe.
**Why this order:** like changing the lock on a door. Put the new lock in and check the new key works before you remove the old lock, so you are never locked out.

1. Make a new key pair.
2. Add the new lock to the host, in `/root/.ssh/authorized_keys`, with the same restrictions as the old one (the part starting `restrict,command="/usr/local/bin/ci-deploy-watchdog.sh",...`).
3. In GitHub, replace the `DEPLOY_SSH_KEY` secret with the new private key.
4. Push a small change to a watchdog script and check the Deploy run is green.
5. Only now, delete the old lock line from `authorized_keys`.

### Replace the Tailscale credentials (rotate them)
**When:** you think the secret leaked, or you lost it.
**Why this order:** same idea. Make the new one, check it works, then delete the old one.

1. In Tailscale, create a new OAuth client. Give it `auth_keys` write access and the tag `tag:ci-deploy` only.
2. In GitHub, replace `TS_OAUTH_CLIENT_ID` and `TS_OAUTH_SECRET`.
3. Check that Deploy is green.
4. Delete the old client in Tailscale.

### Add a new script to the pipeline
**When:** you write a third watchdog.
**Why so many steps:** four places have to agree about the new script. If you miss one, the deploy is refused, and that is on purpose.

1. Put the script in `HomeLab/5 - Automation/scripts/`.
2. On the host, create the script's `.service` and `.timer` files. The pipeline does not make these.
3. On the host, add the script and unit names to the approved lists in `ci-deploy-watchdog.sh` (`ALLOWED_SCRIPTS` and `ALLOWED_UNITS`). This file cannot update itself, so you copy it over yourself with your own key.
4. In `deploy.yml`, add the script to the `paths:` list and add a deploy step for it.

## Troubleshooting

| You see | Look at this first |
|---|---|
| CI red, message says `syntax error` | The script is written wrongly. The log gives the file and line number. |
| CI red, message has a code like `SC2164` | ShellCheck warning. Search the code to read the explanation. |
| The Deploy run did not start | It only runs when you push to `main` and change one of the two watchdog scripts. |
| Deploy fails at the Tailscale step | The Tailscale ID or secret is wrong or deleted, or its name in GitHub does not match `deploy.yml` exactly. |
| `Permission denied (publickey)` | The `DEPLOY_SSH_KEY` secret is wrong or cut short (missing the BEGIN or END line), or the matching lock is not on the host. |
| `denied: script/unit not on allowlist` | The script name is not on the host's approved list. |
| `denied: uploaded script fails bash -n` | The host checked the script and it has a syntax error. Fix the script. |
| You cannot reach Proxmox after editing Tailscale rules | A device is tagged and no longer counts as one of your own. Check the Machines page. |

# Change Log

### 2026-09-22: Setup finished, first deploy checked

Finished the manual steps: Tailscale rules, OAuth client, three GitHub secrets, and the move to `tailscale/github-action@v4`. Before pushing, the new commits were scanned for secrets (none found). Pushed 4 commits to `main`: CI green, Deploy green.

Then checked the host:

| Check | Result |
|---|---|
| `fix-orphan-taps.sh` fingerprint | `e8f10725ebc993d1985a679f6abedf23ebc60f342ae299e0d1b55122a7c08944`, same on repo and host |
| `fix-down-interfaces.sh` fingerprint | `5522de2d825560dd44db1bc23804e2ac25e079efb5e81e31a7113578d75113f0`, same on repo and host |
| File dates on the host | `2026-09-22 02:30`, the deploy time |
| Timers | Both running. `fix-orphan-taps.service` finished on schedule and reported `tap101i1 tiene master`. |

SSH from the PC to Proxmox still worked after the Tailscale rules were narrowed.

### 2026-09-18: Pipeline built

CI workflow, deploy workflow, `deploy.sh`, the host wrapper, and the restricted deploy key were built and tested. Earlier detail: [[Proxmox Administration]].
