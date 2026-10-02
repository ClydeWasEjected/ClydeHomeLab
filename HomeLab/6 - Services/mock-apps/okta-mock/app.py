#!/usr/bin/env python3
"""
Fake Okta OIDC provider for red-team testing.
Simulates an unauthorized Okta instance to test:
  - Conditional access detection
  - Auth log detection of fake OIDC endpoints
  - App registration abuse detection
"""

from flask import Flask, request, jsonify
import jwt
import json
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Fake issuer (deliberately different from real Okta domain)
FAKE_ISSUER = "https://malicious-okta.internal/oauth2/default"
FAKE_CLIENT_ID = "0oa1a2b3c4d5e6f7g8h9i"

@app.route('/.well-known/openid-configuration', methods=['GET'])
def openid_config():
    """OIDC discovery endpoint — tells clients where to get tokens."""
    config = {
        "issuer": FAKE_ISSUER,
        "authorization_endpoint": "http://localhost:5001/oauth2/authorize",
        "token_endpoint": "http://localhost:5001/oauth2/token",
        "userinfo_endpoint": "http://localhost:5001/oauth2/userinfo",
        "jwks_uri": "http://localhost:5001/.well-known/jwks.json",
        "scopes_supported": ["openid", "profile", "email"],
        "response_types_supported": ["code", "id_token", "token"],
    }
    app.logger.info(f"[OIDC Discovery] Client: {request.remote_addr} requested config")
    return jsonify(config)

@app.route('/oauth2/token', methods=['POST'])
def token():
    """Token endpoint — issues fake JWT tokens."""
    grant_type = request.form.get('grant_type')
    client_id = request.form.get('client_id')
    username = request.form.get('username', 'unknown@malicious')
    code = request.form.get('code', 'fake_code')

    app.logger.warning(f"[TOKEN REQUEST] client_id={client_id}, grant_type={grant_type}, "
                       f"user={username}, source={request.remote_addr}")

    # Fake JWT payload
    payload = {
        "iss": FAKE_ISSUER,
        "sub": username,
        "aud": FAKE_CLIENT_ID,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "auth_time": int(datetime.utcnow().timestamp()),
        "amr": ["pwd"],
    }

    # Sign with local secret (not real Okta key)
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    response = {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": token,
        "scope": "openid profile email"
    }
    return jsonify(response)

@app.route('/oauth2/authorize', methods=['GET'])
def authorize():
    """Authorization endpoint — simulates login flow."""
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope', 'openid')

    app.logger.warning(f"[AUTH REQUEST] client_id={client_id}, redirect_uri={redirect_uri}, "
                       f"scope={scope}, source={request.remote_addr}")

    # In a real phishing scenario, this would return a fake login page
    return f"""
    <html><body>
    <h1>Okta Login (FAKE)</h1>
    <p>This is a fake Okta instance for lab testing.</p>
    <p>Client: {client_id}</p>
    <p>Redirect: {redirect_uri}</p>
    </body></html>
    """

@app.route('/oauth2/userinfo', methods=['GET'])
def userinfo():
    """Userinfo endpoint — returns fake user claims."""
    auth_header = request.headers.get('Authorization', '')
    app.logger.info(f"[USERINFO] Authorization header present: {bool(auth_header)}, "
                    f"source={request.remote_addr}")

    return jsonify({
        "sub": "00u1a2b3c4d5e6f7g8h9i",
        "name": "Fake User",
        "email": "fake@malicious-okta.internal",
        "email_verified": True,
    })

@app.route('/.well-known/jwks.json', methods=['GET'])
def jwks():
    """JWKS endpoint — publishes fake signing keys."""
    app.logger.info(f"[JWKS] JWKS requested by {request.remote_addr}")
    return jsonify({
        "keys": [
            {
                "kty": "oct",
                "kid": "fake-key-1",
                "use": "sig",
                "alg": "HS256",
            }
        ]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "okta-mock"})

if __name__ == '__main__':
    # Log all requests
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        filename='/tmp/okta-mock.log'
    )
    app.run(host='0.0.0.0', port=5001, debug=False)
