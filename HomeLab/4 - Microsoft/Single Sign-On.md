# Single Sign-On (Entra and Okta)

Related: [[Active Directory Design]] · [[AD Administration]]

SSO round trips through two identity providers: Microsoft Entra ID (SAML and OIDC) and a free Okta Integrator org (OIDC), plus MFA enforced on the Okta side. Playbook module E2.

## Current State

**Entra ID (SAML)**

| Item | Value |
|---|---|
| App | Microsoft Entra SAML Toolkit (gallery, SP-initiated variant), Enterprise application |
| Identifier (Entity ID) | `https://samltoolkit.azurewebsites.net` |
| Reply URL (ACS) | `https://samltoolkit.azurewebsites.net/SAML/Consume` |
| Sign on URL | `https://samltoolkit.azurewebsites.net/` |
| Assigned to | `SG_Entra_Pilot` |
| Toolkit side | Needs a user registered on the toolkit site matching the Entra user's email before SP-initiated login works |

**Entra ID (OIDC)**

| Item | Value |
|---|---|
| App registration | `OIDC-Toolkit-Test`, single tenant |
| Redirect URI (Web) | `https://jwt.ms` |
| ID tokens (implicit) | Enabled |
| Delegated permissions | `openid`, `profile`, `email` (plus default `User.Read`) |
| Test | Browse to the v2.0 authorize endpoint with `response_type=id_token`, land on jwt.ms |

![[e2-entra-oidc-permissions.png]]

**Okta (Integrator Free Plan org)**

| Item | Value |
|---|---|
| Org | Okta Integrator Free Plan (no 30-day expiry). Org URL and Client ID are not recorded here on purpose |
| Test user | `Miguel Ruiz`, Active, password set by admin, email is a plus-alias of a personal address |
| Group | `SG_Okta_Pilot`, contains the test user |
| App | `oidcdebugger-OIDC`, OIDC Web Application |
| Sign-in redirect URI | `https://oidcdebugger.com/debug` |
| Grant types | Authorization Code (default), Implicit (hybrid) with ID token allowed |
| Assignment | `SG_Okta_Pilot` |
| Authentication policy | `Pilot MFA`, attached to `oidcdebugger-OIDC` |
| Rule 1 `OktaPilot` | IF group `SG_Okta_Pilot`: password + another factor, Phishing resistant off, Require user interaction (any), re-auth every 1 hour |
| Rule 2 Catch-all | Any request: any 2 factor types (policy default) |
| Second factor | Okta Verify |

![[e2-okta-oidc-idtoken.png]]

<sub>Okta debugger run with `response_type=id_token`: authorization server responded with tokens, state matched.</sub>

**Entra vs Okta, same kind of task**

| Topic | Entra | Okta |
|---|---|---|
| Where apps live | Enterprise applications (SAML) and App registrations (OIDC), two places | Applications > Create App Integration, protocol picked in the wizard |
| Access control | Conditional Access (CA001) scoped to a group | Authentication policy attached per app, rules scoped to a group |
| SAML flow | SP-initiated needs a Sign on URL, IdP-initiated via My Apps | Not built, module moved to OIDC (see Change Log) |
| OIDC flow | Client-initiated via hand-built authorize URL, token decoded at jwt.ms | Client-initiated via oidcdebugger.com, default response type is `code`, `id_token` must be chosen |
| Failure diagnosis | On-screen error pages, sign-in logs not used | System Log gives the exact policy or enrollment reason |

**Open items**
- The Okta admin account uses an institutional email that may be deactivated after graduation. Move it to a permanent address, add a second super admin and a second MFA factor.
- Okta setup that needs a business email domain: a domain (about 10 EUR per year) would also allow a verified custom domain in Entra.

## Change Log

- **2026-09-29**: Built E2. Entra SAML Toolkit app, `OIDC-Toolkit-Test` registration, Okta org, `SG_Okta_Pilot`, `oidcdebugger-OIDC`, `Pilot MFA` policy.
  - Okta signup rejected Gmail as a non-business email. The org was created with an institutional address instead.
  - **samltest.id is no longer usable.** The domain now serves a "domain for sale" page whose script redirects browsers to ad domains. DNS on pfSense and on 1.1.1.1 both returned the same public IP, and a plain request got HTTP 410, so the redirect is the site itself, not the lab network and not a browser extension. The Okta half of the module was rebuilt from SAML to OIDC with oidcdebugger.com.
  - First Okta sign-in was denied with `access_denied` (System Log: "policy requirements could not be satisfied by the user's current set of available authenticator enrollments"). Cause: the `OktaPilot` rule accepted only Okta Verify FastPass with the phishing-resistant constraint. Fixed by unticking Phishing resistant so a normal Okta Verify enrollment satisfies the rule.
  - Signing in as the test user at the plain Okta dashboard proves nothing about the app rule. The dashboard uses another policy, so the test has to start from the debugger's Send Request.
  - The test user also hit the Okta Admin Console and got 403, as expected for a non-admin.
  - Verification: debugger with `response_type=id_token` returned tokens and matching state (screenshot above). A `code` response type run after the policy applied also succeeded.

## Not evidenced

- jwt.ms decoded token for the Entra OIDC test (s2d).
- Decoded SAML attributes on the SAML Toolkit page (s1d); only the toolkit landing page was captured.
- The Okta Verify challenge screen on the second sign-in (s3f). The policy and rule were seen live, and the second sign-in succeeded, but no screenshot of the prompt exists.
- jwt.ms decode of the Okta ID token and its `email` claim.
- Entra-side facts (app settings, assignments) were read from playbook steps and screenshots, not cross-checked against the tenant.
