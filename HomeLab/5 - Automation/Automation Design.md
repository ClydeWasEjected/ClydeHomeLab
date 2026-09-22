**Scope:** how scripts get from this repo onto `proxmox-a8` without manual copying. Covers the CI/CD pipeline and its security model. Operating procedures live in [[Automation Administration]]. The scripts themselves are described in [[Proxmox Administration]].

# Current State (as of 2026-09-22)

## Purpose

Watchdog scripts used to exist only on the Proxmox host, edited by hand, so fixes were lost and nothing checked them. The repo is now the source of truth: a change is written here, checked automatically, and deployed automatically.

## Flow

```
edit script -> git push
   -> CI  (ci.yml): bash -n + shellcheck on every *.sh, on push and PR
   -> Deploy (deploy.yml): on push to main touching a watchdog script
        GitHub runner joins the tailnet as an ephemeral node (tag:ci-deploy)
        writes the deploy key from a GitHub secret
        deploy.sh: bash -n locally, then ssh to proxmox-a8 with the restricted key
        ci-deploy-watchdog.sh (on the host): allowlist check, bash -n, install, restart timer
```

## Components

| Component | Location | Role |
|---|---|---|
| CI workflow | `.github/workflows/ci.yml` | Syntax and lint gate |
| Deploy workflow | `.github/workflows/deploy.yml` | Tailscale join, key write, deploy both scripts |
| Deploy script | `HomeLab/5 - Automation/scripts/deploy.sh` | One deploy path, used locally and by CI |
| Forced-command wrapper | `HomeLab/5 - Automation/scripts/ci-deploy-watchdog.sh`, installed at `/usr/local/bin/` on the host | Only entry point for the deploy key |
| Watchdogs | `HomeLab/5 - Automation/scripts/fix-orphan-taps.sh`, `fix-down-interfaces.sh` | What gets deployed |

`.github/workflows/` stays at the repo root because GitHub only reads workflows from there.

## Security model

The deploy path assumes any single layer can fail. Each layer limits what the next one can do.

| Layer | Control | Limit it enforces |
|---|---|---|
| GitHub | Secrets stored encrypted, redacted in logs. Fork PR workflows require approval. | No secret reaches code from outside the repo |
| Tailscale policy | Grant `tag:ci-deploy` to `100.121.216.124` on `tcp:22` only. The default allow-all rule was narrowed from `*` to `autogroup:member` so tagged machines get nothing else. | The runner can reach Proxmox SSH and nothing else on the tailnet |
| Tailscale policy tests | Assertions in the policy: the tag can reach Proxmox:22 and cannot reach the PC. Tailscale refuses to save a policy that fails them. | A policy edit cannot silently widen access |
| OAuth client | Scope `auth_keys` write, restricted to `tag:ci-deploy`. Mints short-lived node keys. | No long-lived join credential exists |
| SSH key | Dedicated ed25519 key, `restrict,command="/usr/local/bin/ci-deploy-watchdog.sh"` in `authorized_keys` | The key cannot open a shell, forward ports, or run any other command |
| Wrapper | Accepts only `deploy <script> <unit>` from a hardcoded allowlist, refuses anything failing `bash -n` | A leaked key can install one of two known scripts, and only if they parse |

Verified 2026-09-18: `whoami` and `cat /etc/shadow` through the deploy key are refused, and an off-allowlist script name is refused.

## Design decisions

| Decision | Why |
|---|---|
| Repo stays public | History scanned before the first push: no private keys or tokens. Only the tailnet address `100.121.216.124` is exposed, and it is reachable only inside the tailnet. The pipeline is also the strongest portfolio piece in the repo. |
| Automation gets its own folder (`5 - Automation`) | Scripts and pipeline are their own domain and will grow beyond Proxmox (AD provisioning, PowerShell). |
| Deploy both scripts on any change | Idempotent: redeploying an unchanged script is harmless, and it avoids diffing logic. |
| Dedicated key and OAuth client, not personal credentials | Each can be revoked without touching anything else. |
| Actions pinned to a major version tag (`@v4`) | Gets fixes without surprise breaking changes. |
| Scripts pinned to LF in `.gitattributes` | Windows `autocrlf` would otherwise add CRLF and break the shebang on Linux. |

## Known limits

- The allowlist exists in two places: the wrapper on the host and the steps in `deploy.yml`. Adding a script means updating both.
- The wrapper cannot update itself. It is installed by hand, using a personal key, whenever it changes.
- The pipeline deploys scripts only. The systemd `.service` and `.timer` units were created by hand and are not managed here.
- The key lands on the host as root. The restrictions above are what make that acceptable; a dedicated low-privilege user would be tighter.
- No automatic rollback. Recovery is reverting the commit and pushing.
- Third-party actions are pinned by version tag, not commit hash.
- Failures are visible only in the GitHub Actions tab. No alerting.

# Change Log

### 2026-09-22: First real deploy

Pipeline built 2026-09-18 and moved to `5 - Automation` on 2026-09-19. Setup completed 2026-09-22: Tailscale tag, grants and tests, OAuth client, three GitHub secrets, `tailscale/github-action` bumped from `@v3` to `@v4` after checking its README (input names unchanged). Pushed to `main`: CI and Deploy both green. Verified on the host: SHA-256 of both scripts identical to the repo, files stamped at deploy time, both timers active. See [[Automation Administration]] for the evidence.
