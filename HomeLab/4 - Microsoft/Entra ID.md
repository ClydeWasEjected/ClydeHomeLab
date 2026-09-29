# Entra ID (identities, RBAC, Conditional Access, MFA)

Related: [[AD Administration]] · [[Single Sign-On]]

The cloud-native equivalent of the on-prem AD access model in [[AD Administration]]: principals, RBAC roles instead of GPO delegation, and Conditional Access as the policy engine instead of Group Policy. Playbook module E1.

## Current State

**Tenant and licensing**

| Item | Value |
|---|---|
| Tenant type | Azure free account with self-service Microsoft Entra ID P2 trial activated |
| Primary domain | `<tenantname>.onmicrosoft.com` (no custom domain added) |
| Trial length | 30 days from activation |
| Trial billing | Card on file required, auto-renews to a paid monthly subscription unless cancelled before the renewal date shown at activation |
| Why P2 and not the free tier | Conditional Access and non-gallery SSO app configuration are Premium (P1/P2) features; the default tenant from an Azure free account starts on the Free tier |

**Identities, groups, and roles**

| Object | Type | Scope/Role | Why |
|---|---|---|---|
| bg-admin | User (cloud-only) | Global Administrator, excluded from every Conditional Access policy | Created before CA001 existed, so a policy misconfiguration cannot lock out the only admin account. |
| jhana.villanueva, cayden.laquindanum, robert.greene, eric.ries | User | Members of `SG_Entra_Pilot` | Test/pilot users for CA and MFA validation. |
| `SG_Entra_Pilot` | Security group (assignment-based) | Holds the 4 test users | Access is granted by group membership, never by naming a user directly in a role or policy. |
| `SG_Entra_Pilot_Admins` | Security group (role-assignable) | Carries the Helpdesk Administrator role | Least-privilege admin role assigned to the group, not Global Administrator, matching the RBAC scoping used for delegation in [[AD Administration]]. Kept separate from `SG_Entra_Pilot` on purpose: a group used to test CA/MFA on ordinary users should not also carry an admin role. |
| `CA001-Require-MFA-Pilot` | Conditional Access policy | Included `SG_Entra_Pilot`, excluded `bg-admin`, all cloud apps | Policy is the enforcement point in the cloud; built Report-only first, confirmed, then turned On. |
| Security info (Microsoft Authenticator) | MFA registration | Jhana Villanueva | Registration and enforcement are two separate steps, both required. |

**Conditional Access policy: CA001-Require-MFA-Pilot**

| Setting | Value |
|---|---|
| Users included | `SG_Entra_Pilot` |
| Users excluded | `bg-admin` |
| Cloud apps | All cloud apps |
| Grant control | Require multifactor authentication |
| State | On (built and confirmed in Report-only first) |

**MFA registration and proof**

| Item | Value |
|---|---|
| Method registered | Microsoft Authenticator, Jhana Villanueva |
| Enforcement proof | Sign-in log entry for CA001-Require-MFA-Pilot, result Success |

![[e1-mfa-enforced-success.png]]

## Change Log

**2026-09-29**: Built E1. Activated the Entra ID P2 trial on an Azure free tenant, created the `bg-admin` break-glass account excluded from Conditional Access, created 4 test users and `SG_Entra_Pilot`, created `CA001-Require-MFA-Pilot` in Report-only mode and then turned it On, registered an MFA method for one pilot user.

- **Role-assignable groups can only be flagged at creation, never after.** `SG_Entra_Pilot` was rejected outright in the Helpdesk Administrator role-assignment search ("0 results found, only groups eligible for role assignment are displayed"). Fixed by creating a second group, `SG_Entra_Pilot_Admins`, with the role-assignable option turned on at creation, and assigning the role there instead. This also matches least privilege better: the group used to test CA/MFA on ordinary users should not also carry an admin role.
- **Security Defaults blocks custom Conditional Access from evaluating at all.** The first sign-in test as Jhana showed only `Security Defaults` (Enabled, Result Not Applied) on the Conditional Access tab; `CA001` did not appear, report-only or otherwise. Microsoft does not evaluate the two together. Fixed by disabling Security Defaults (Identity > Properties > Manage Security Defaults) and signing in again: the new sign-in showed `CA001-Require-MFA-Pilot`, Policy state Report-only, Result "Report-only: User action required", User and Resource both Matched.
- Verification: the Report-only hit above and the enforced Success result (screenshot) together confirm the policy moved from "would have required MFA" to "actually required and satisfied MFA" once switched On.

## Not evidenced

- Microsoft Entra ID P2 listed with trial expiry date under Licensed features (s0a): no direct screenshot captured at that exact step; the trial checkout screen and a later Licenses check are the closest recorded confirmation.
- `SG_Entra_Pilot_Admins` flagged as role-assignable (s2a): no screenshot of the toggle itself.
- Helpdesk Administrator shown on the user's Assigned roles blade with source `SG_Entra_Pilot_Admins`, not Direct (s2c): no screenshot.
- `CA001-Require-MFA-Pilot` shown as state On in the policies list (s3c): no screenshot; the On state is inferred from the enforced Success result in the final sign-in test.
- Tenant facts (licenses, group flags, role sources) were read from playbook steps, chat troubleshooting, and screenshots, not independently cross-checked against the tenant via API: there is no read-only Graph credential set up for this tenant yet, unlike AD's read-only LDAP account used for [[AD Administration]] checkpoints.
</content>
