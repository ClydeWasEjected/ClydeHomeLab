# Mock OAuth Apps for Red-Team Testing

Lab-grade fake OAuth/OIDC providers to test detection of unauthorized app registration and malicious OAuth flows.

## Apps

### 1. Okta Mock (Port 5001)

Simulates an unauthorized Okta OIDC instance to test:
- Conditional access detection of fake OIDC endpoints
- Auth log detection when users auth against unexpected issuers
- App registration abuse (registering an app with a fake Okta tenant)

Endpoints:
- `GET /.well-known/openid-configuration` - OIDC discovery
- `GET /oauth2/authorize` - Authorization endpoint
- `POST /oauth2/token` - Token endpoint (issues fake JWTs)
- `GET /oauth2/userinfo` - User info endpoint
- `GET /.well-known/jwks.json` - Public keys

Test scenario:
```bash
# 1. Discover OIDC config (what a legitimate app would do)
curl http://localhost:5001/.well-known/openid-configuration

# 2. Check if AD logs detect the OIDC discovery
# 3. Check if Entra ID app registration catches an app pointing to this issuer
# 4. Can conditional access block it?
```

### 2. Slack Mock (Port 5002)

Simulates a malicious Slack app requesting excessive permissions to test:
- OAuth consent log detection
- Permission audit trails
- Scope abuse detection

Endpoints:
- `GET /oauth/authorize` - Authorization with excessive scopes
- `POST /oauth/authorize` - Consent submission
- `POST /oauth/token` - Token exchange
- `GET /oauth/callback` - Redirect callback
- `GET /oauth/flows` - Audit log of all OAuth flows (for validation)

Malicious scopes requested:
- `users:read` - List all users
- `users.profile:read` - Read user profiles
- `conversations:read` - List channels
- `groups:read` - Read private channels
- `im:read` - Read DMs
- `mpim:read` - Read group DMs
- `files:read` - Read file metadata
- `admin` - Admin access
- More

Test scenario:
```bash
# 1. User (or attacker) starts OAuth flow
curl "http://localhost:5002/oauth/authorize?client_id=attacker&redirect_uri=http://attacker.com/callback&scope=users:read,conversations:read"

# 2. Check if Slack logs capture excessive scope requests
# 3. Check if Entra ID app audit logs show the registration
# 4. Can you detect this in your SIEM?

# 5. View all flows for testing
curl http://localhost:5002/oauth/flows | jq
```

## Setup

```bash
pip install -r requirements.txt

# Terminal 1: Run Okta mock
python okta-mock/app.py

# Terminal 2: Run Slack mock
python slack-mock/app.py
```

Logs go to `/tmp/okta-mock.log` and `/tmp/slack-mock.log`.

## Test Plan

1. **App Registration Abuse**: Entra ID app gallery or manual registration
   - Register an app pointing to `http://localhost:5001` as OIDC issuer
   - Can conditional access block it?
   - Does auth log show the attempt?

2. **OAuth Scope Abuse**: Slack app directory or direct OAuth
   - Trigger Slack OAuth flow
   - Check if audit logs show excessive scopes
   - Can you detect this in M365 audit logs?

3. **Detection Validation**
   - Check Windows Event Viewer: sign-in logs, app activity
   - Check Entra ID: app activity, app registrations, audit logs
   - Check Slack (if integrated): app audit logs
   - Check SIEM (when deployed): auth attempts, app registration events

## Detection Goals

For each app, the test loop is: **attack → log → detect → remediate**.

- Can you spot the fake Okta OIDC issuer in logs?
- Can you detect excessive OAuth scope requests?
- Can conditional access policies stop it before token issue?
- What audit trail does the attack leave?

This is the red side. The defense side (detecting these) is what matters long-term.

## Notes

- These are lab-only, intentionally fake (HS256 signing, no real crypto)
- Run on localhost only (not exposed to LAN/internet)
- For integration testing, use AD/Slack test workspaces, not production
- Logs include source IP, timestamp, client_id, scopes for audit

## See Also

- [Identity Design.md](../../Microsoft/Identity%20Design.md) - Entra ID architecture
- [Microsoft Administration.md](../../Microsoft/Microsoft%20Administration.md) - AD policies
