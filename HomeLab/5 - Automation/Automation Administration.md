**Scope:** operating the deploy pipeline. Architecture and reasoning are in [[Automation Design]].

# Current State (as of 2026-09-22)

## Credentials

Nothing secret is stored in this repo.

| Name | Where it lives | What it is | Created |
|---|---|---|---|
| `DEPLOY_SSH_KEY` | GitHub repo secret. Source file on the PC: `C:\Users\Clyde\.ssh\deploy-keys\homelab-ci-deploy` | Private half of the deploy key. Public half is in `/root/.ssh/authorized_keys` on `proxmox-a8`, restricted. Fingerprint `SHA256:OVcs3Lf6ZgdsgKNRV2573qRpfKMiv/xkD/4Y4w8esU4`. | 2026-09-18 |
| `TS_OAUTH_CLIENT_ID` | GitHub repo secret | Tailscale OAuth client ID (`github-actions-homelab-deploy`) | 2026-09-22 |
| `TS_OAUTH_SECRET` | GitHub repo secret | Tailscale OAuth client secret. Shown once at creation, cannot be read back. | 2026-09-22 |

Tailscale policy entries: `tagOwners` for `tag:ci-deploy`, a grant from that tag to `100.121.216.124` on `tcp:22`, and two policy tests. The original allow-all grant now uses `autogroup:member` as its source.

## Routine tasks

**Deploy a script by hand** (same path CI uses):
```
bash "HomeLab/5 - Automation/scripts/deploy.sh" <script-name> <unit-name> [key-path]
```
Example: `deploy.sh fix-orphan-taps.sh fix-orphan-taps`. The key defaults to the deploy key above.

**Check that the host matches the repo:**
```
sha256sum "HomeLab/5 - Automation/scripts/"fix-*.sh
ssh root@100.121.216.124 "sha256sum /usr/local/bin/fix-*.sh"
```
The hashes must be identical.

**Check the watchdogs are running:**
```
ssh root@100.121.216.124 "systemctl list-timers 'fix-*' --no-pager; journalctl -u fix-orphan-taps.service -n 3 --no-pager"
```

## Procedures

**Rotate the deploy key**
1. Generate a new ed25519 key pair.
2. Add the new public key to `/root/.ssh/authorized_keys` on the host with the same `restrict,command="/usr/local/bin/ci-deploy-watchdog.sh",...` prefix.
3. Replace the `DEPLOY_SSH_KEY` secret with the new private key.
4. Push a small change to a watchdog script and confirm Deploy is green.
5. Remove the old public key line from `authorized_keys`.

**Rotate the Tailscale OAuth client**
1. Create a new OAuth client: scope `auth_keys` write, tag `tag:ci-deploy` only.
2. Replace `TS_OAUTH_CLIENT_ID` and `TS_OAUTH_SECRET`.
3. Confirm Deploy is green, then delete the old client.

**Add a new script to the pipeline**
1. Add the script under `HomeLab/5 - Automation/scripts/`.
2. Create its `.service` and `.timer` on the host (the pipeline does not manage units).
3. Add the script and unit names to `ALLOWED_SCRIPTS` and `ALLOWED_UNITS` in `ci-deploy-watchdog.sh`, then install that file on the host with a personal key. It cannot deploy itself.
4. Add the path to `paths:` in `deploy.yml` and add a deploy step.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| CI red, `syntax error` from `bash -n` | Real syntax error in a script. The log names the file and line. |
| CI red, `SCxxxx` from ShellCheck | ShellCheck warning. The code links to an explanation. |
| Deploy did not run | Its `paths:` filter only matches the two watchdog scripts, and it runs only on push to `main`. |
| Deploy fails at the Tailscale step | OAuth client wrong or deleted, tag not in `tagOwners`, or a secret name that does not match `deploy.yml` exactly. |
| Deploy fails with `Permission denied (publickey)` | `DEPLOY_SSH_KEY` is wrong or incomplete (missing BEGIN or END line), or the public key is not in `authorized_keys`. |
| `denied: script/unit not on allowlist` | Script or unit name missing from the wrapper's allowlist on the host. |
| `denied: uploaded script fails bash -n` | The wrapper refused a script that does not parse. Fix the script. |
| Lost SSH access to Proxmox after a Tailscale policy edit | The policy tests failed to catch it, or a device is tagged and no longer in `autogroup:member`. Check the Machines page. |

# Change Log

### 2026-09-22: Setup completed, first deploy verified

Completed the manual steps: Tailscale policy, OAuth client, three GitHub secrets. Bumped `tailscale/github-action` to `@v4`. Before pushing, scanned the unpushed commits for secrets (none). Only `100.121.216.124` and `192.168.0.0` appear in them.

Pushed to `main` (4 commits): CI green, Deploy green.

Verification on `proxmox-a8` after the deploy:
- `fix-orphan-taps.sh` SHA-256 `e8f10725ebc993d1985a679f6abedf23ebc60f342ae299e0d1b55122a7c08944`, identical on repo and host
- `fix-down-interfaces.sh` SHA-256 `5522de2d825560dd44db1bc23804e2ac25e079efb5e81e31a7113578d75113f0`, identical on repo and host
- Both files stamped `2026-09-22 02:30` on the host, the deploy time
- Both timers active. `fix-orphan-taps.service` finished successfully on schedule and reported `tap101i1 tiene master`.

Also on 2026-09-22, SSH to `proxmox-a8` from the PC still worked after narrowing the Tailscale allow-all grant to `autogroup:member`.

### 2026-09-18: Pipeline built

CI workflow, deploy workflow, `deploy.sh`, the forced-command wrapper, and the restricted deploy key created and tested locally. See [[Proxmox Administration]] for the earlier detail.
