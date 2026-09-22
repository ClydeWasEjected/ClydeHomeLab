> [!NOTE] At a glance
> How to run the deploy pipeline day to day. Why it is built this way: [[Automation Design]].
> Most common tasks: [[#Deploy by hand]] and [[#Check the host matches the repo]].

# Current State (as of 2026-09-22)

## Credentials

Nothing secret is stored in this repo.

| Name | Lives in | What it is |
|---|---|---|
| `DEPLOY_SSH_KEY` | GitHub secret (source file on the PC: `C:\Users\Clyde\.ssh\deploy-keys\homelab-ci-deploy`) | Private half of the deploy key. Public half is in `authorized_keys` on the host, restricted. |
| `TS_OAUTH_CLIENT_ID` | GitHub secret | Tailscale OAuth client ID, named `github-actions-homelab-deploy` |
| `TS_OAUTH_SECRET` | GitHub secret | Its secret. Shown once at creation, cannot be read back. |

Deploy key fingerprint: `SHA256:OVcs3Lf6ZgdsgKNRV2573qRpfKMiv/xkD/4Y4w8esU4`. Created 2026-09-18.

Tailscale side: a `tagOwners` entry for `tag:ci-deploy`, one grant from that tag to `100.121.216.124` on `tcp:22`, two policy tests, and the original allow-all grant narrowed to `autogroup:member`.

## Everyday commands

### Deploy by hand

Same path CI uses.

```
bash "HomeLab/5 - Automation/scripts/deploy.sh" <script-name> <unit-name>
```

Example: `deploy.sh fix-orphan-taps.sh fix-orphan-taps`

### Check the host matches the repo

```
sha256sum "HomeLab/5 - Automation/scripts/"fix-*.sh
ssh root@100.121.216.124 "sha256sum /usr/local/bin/fix-*.sh"
```

The two lists of hashes must be identical.

### Check the watchdogs are running

```
ssh root@100.121.216.124 "systemctl list-timers 'fix-*' --no-pager"
ssh root@100.121.216.124 "journalctl -u fix-orphan-taps.service -n 3 --no-pager"
```

## Procedures

### Rotate the deploy key

1. Generate a new ed25519 key pair.
2. Add the new public key to `/root/.ssh/authorized_keys` with the same `restrict,command="/usr/local/bin/ci-deploy-watchdog.sh",...` prefix.
3. Replace the `DEPLOY_SSH_KEY` secret with the new private key.
4. Push a small change to a watchdog and confirm Deploy is green.
5. Delete the old public key line.

### Rotate the Tailscale OAuth client

1. Create a new client: scope `auth_keys` write, tag `tag:ci-deploy` only.
2. Replace `TS_OAUTH_CLIENT_ID` and `TS_OAUTH_SECRET`.
3. Confirm Deploy is green, then delete the old client.

### Add a new script to the pipeline

1. Add the script under `HomeLab/5 - Automation/scripts/`.
2. Create its `.service` and `.timer` on the host. The pipeline does not manage them.
3. Add the script and unit names to `ALLOWED_SCRIPTS` and `ALLOWED_UNITS` in `ci-deploy-watchdog.sh`, then install that file on the host with a personal key. It cannot deploy itself.
4. Add the path to `paths:` in `deploy.yml`, and a deploy step.

## Troubleshooting

| You see | Check first |
|---|---|
| CI red: `syntax error` | A real syntax error. The log names the file and line. |
| CI red: `SCxxxx` | A ShellCheck warning. The code links to an explanation. |
| Deploy did not run | It only runs on a push to `main` that touches the two watchdog scripts. |
| Deploy fails at the Tailscale step | OAuth client wrong or deleted, tag missing from `tagOwners`, or a secret name that does not match `deploy.yml`. |
| `Permission denied (publickey)` | `DEPLOY_SSH_KEY` is wrong or incomplete (missing BEGIN or END line), or its public key is not in `authorized_keys`. |
| `denied: script/unit not on allowlist` | The name is missing from the wrapper's allowlist on the host. |
| `denied: uploaded script fails bash -n` | The wrapper refused a script that does not parse. Fix the script. |
| Lost SSH to Proxmox after a policy edit | A device is tagged and no longer in `autogroup:member`. Check the Machines page. |

# Change Log

### 2026-09-22: Setup completed, first deploy verified

Finished the manual steps: Tailscale policy, OAuth client, three GitHub secrets, `@v4` bump. The unpushed commits were scanned for secrets first (none; only `100.121.216.124` and `192.168.0.0` appear). Pushed 4 commits to `main`: CI green, Deploy green.

Checked on `proxmox-a8` afterwards:

| Check | Result |
|---|---|
| `fix-orphan-taps.sh` SHA-256 | `e8f10725ebc993d1985a679f6abedf23ebc60f342ae299e0d1b55122a7c08944`, same on repo and host |
| `fix-down-interfaces.sh` SHA-256 | `5522de2d825560dd44db1bc23804e2ac25e079efb5e81e31a7113578d75113f0`, same on repo and host |
| File timestamps on host | `2026-09-22 02:30`, the deploy time |
| Timers | Both active. `fix-orphan-taps.service` finished on schedule and reported `tap101i1 tiene master`. |

Also that day: SSH from the PC still worked after narrowing the Tailscale allow-all grant to `autogroup:member`.

### 2026-09-18: Pipeline built

CI workflow, deploy workflow, `deploy.sh`, the wrapper, and the restricted deploy key were created and tested locally. Earlier detail: [[Proxmox Administration]].
