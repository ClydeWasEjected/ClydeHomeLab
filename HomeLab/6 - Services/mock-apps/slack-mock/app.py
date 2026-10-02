#!/usr/bin/env python3
"""
Fake Slack app for red-team testing.
Simulates a malicious Slack app requesting excessive permissions to test:
  - Entra ID app permission audit detection
  - OAuth consent screen abuse
  - App registration abuse logs
"""

from flask import Flask, request, jsonify, redirect
import secrets
import json
from datetime import datetime
from urllib.parse import urlencode

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Fake Slack app details
FAKE_SLACK_APP_ID = "A01A2B3C4D5"
FAKE_SLACK_CLIENT_SECRET = secrets.token_hex(32)
REDIRECT_URL = "http://localhost:5002/oauth/callback"

# Excessive permissions for red-team testing
MALICIOUS_SCOPES = [
    "users:read",           # Read user list
    "users.profile:read",   # Read user profiles
    "conversations:read",   # List all channels
    "groups:read",          # Read private channels
    "im:read",              # Read DMs
    "mpim:read",            # Read group DMs
    "files:read",           # Read file metadata
    "admin",                # Admin access (if available)
    "emoji:read",           # Read emoji list
    "usergroups:read",      # Read user groups
]

# Store OAuth flows for audit
oauth_flows = []

@app.route('/oauth/authorize', methods=['GET'])
def oauth_authorize():
    """
    OAuth authorization endpoint.
    Simulates Slack's permission request screen with excessive scopes.
    """
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri', REDIRECT_URL)
    state = request.args.get('state', secrets.token_hex(16))
    scope = request.args.get('scope', ','.join(MALICIOUS_SCOPES))

    flow_id = secrets.token_hex(8)
    oauth_flows.append({
        "id": flow_id,
        "timestamp": datetime.utcnow().isoformat(),
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scopes": scope.split(','),
        "state": state,
        "source_ip": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', 'unknown'),
    })

    app.logger.warning(
        f"[OAUTH AUTHORIZE] Flow ID: {flow_id}, Client: {client_id}, "
        f"Scopes: {len(scope.split(','))}, Scopes requested: {scope}, "
        f"Source: {request.remote_addr}"
    )

    # Render fake permission consent screen
    scope_list = scope.split(',')
    scope_html = ''.join([f'<li>{s}</li>' for s in scope_list])

    return f"""
    <html>
    <head><title>Slack App Permission (FAKE)</title></head>
    <body>
    <h1>Slack App Permissions (FAKE)</h1>
    <p><strong>App ID:</strong> {client_id}</p>
    <p><strong>Requesting {len(scope_list)} permissions:</strong></p>
    <ul>
    {scope_html}
    </ul>
    <form method="POST" action="/oauth/authorize">
        <input type="hidden" name="state" value="{state}">
        <input type="hidden" name="flow_id" value="{flow_id}">
        <button type="submit" name="approve" value="yes">Approve (for testing)</button>
        <button type="submit" name="approve" value="no">Deny</button>
    </form>
    <hr>
    <p style="font-size: 0.8em; color: #666;">
    Lab Testing Notice: This is a fake Slack app for security testing only.
    Flow ID: {flow_id}
    </p>
    </body>
    </html>
    """

@app.route('/oauth/authorize', methods=['POST'])
def oauth_authorize_submit():
    """Handle consent form submission."""
    flow_id = request.form.get('flow_id')
    state = request.form.get('state')
    approved = request.form.get('approve') == 'yes'

    app.logger.warning(f"[OAUTH CONSENT] Flow: {flow_id}, Approved: {approved}, "
                       f"Source: {request.remote_addr}")

    if not approved:
        return "Authorization denied.", 403

    # Generate authorization code
    auth_code = f"xoxe-{secrets.token_hex(16)}"

    # Redirect back with code + state
    redirect_params = {
        'code': auth_code,
        'state': state,
    }

    # Find the redirect URI from the flow
    flow = next((f for f in oauth_flows if f['id'] == flow_id), None)
    redirect_uri = flow['redirect_uri'] if flow else REDIRECT_URL

    redirect_url = f"{redirect_uri}?{urlencode(redirect_params)}"
    app.logger.info(f"[OAUTH REDIRECT] Sending code to {redirect_uri}")

    return redirect(redirect_url)

@app.route('/oauth/token', methods=['POST'])
def oauth_token():
    """
    Token exchange endpoint.
    Exchanges authorization code for access token.
    """
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    code = request.form.get('code')

    app.logger.warning(f"[TOKEN EXCHANGE] Client: {client_id}, Code: {code[:16]}..., "
                       f"Secret provided: {bool(client_secret)}, Source: {request.remote_addr}")

    if not code or code[:5] != 'xoxe-':
        return jsonify({"error": "invalid_code"}), 400

    # Issue fake access token
    access_token = f"xoxb-{secrets.token_hex(32)}"

    response = {
        "ok": True,
        "access_token": access_token,
        "token_type": "bot",
        "scope": ",".join(MALICIOUS_SCOPES),
        "bot_user_id": "U01A2B3C4D5",
        "app_id": FAKE_SLACK_APP_ID,
        "team": {
            "id": "T01A2B3C4D5",
            "name": "Fake Workspace"
        },
        "enterprise": {
            "id": "E01A2B3C4D5",
            "name": "Fake Enterprise"
        }
    }

    app.logger.info(f"[TOKEN ISSUED] Access token issued for client {client_id}")
    return jsonify(response)

@app.route('/oauth/callback', methods=['GET'])
def oauth_callback():
    """Callback handler for OAuth redirect."""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    app.logger.info(f"[CALLBACK] Code: {code[:16] if code else 'None'}..., "
                    f"State: {state}, Error: {error}, Source: {request.remote_addr}")

    if error:
        return f"<h1>Authorization Error</h1><p>{error}</p>", 400

    if not code:
        return "<h1>Missing authorization code</h1>", 400

    return f"""
    <html>
    <body>
    <h1>OAuth Callback (FAKE Slack)</h1>
    <p>Authorization code received: {code[:20]}...</p>
    <p>State: {state}</p>
    <p>Next step: Exchange code for token at /oauth/token</p>
    </body>
    </html>
    """

@app.route('/oauth/flows', methods=['GET'])
def audit_flows():
    """Return audit log of all OAuth flows (for testing detection)."""
    return jsonify(oauth_flows)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "slack-mock"})

if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        filename='/tmp/slack-mock.log'
    )
    app.run(host='0.0.0.0', port=5002, debug=False)
