# Active Directory Administration

Related: [[Active Directory Design]] · [[DC01]] · [[WIN11-01]]

## Current State (as of 2026-09-16)

### OU Structure
```

ad.jnclydehl.local  
│  
├── Departments  
│ ├── IT  
│ │ ├── Users  
│ │ ├── Computers  
│ │ └── Groups  
│ ├── Security  
│ │ ├── Users  
│ │ ├── Computers  
│ │ └── Groups  
│ └── Operations  
│ ├── Users  
│ ├── Computers  
│ └── Groups  
│  
└── Service Accounts (empty — reserved for C2)

```

> [!todo] Screenshot pending
> Referenced screenshot `aduc-ou-tree-2026-09-16.png` was never actually saved to the attachments folder — add it or drop this callout.

### Security Groups
| Group | Type/Scope | Purpose | Members |
|---|---|---|---|
| SG_IT_Admins | Security, Global | Elevated permissions within IT's scope | *pendiente* |
| SG_IT_Users | Security, Global | Standard IT department users | *pendiente* |
| SG_Security_Analysts | Security, Global | Access to logs/monitoring (future SIEM) | *pendiente* |
| SG_Operations_Users | Security, Global | Standard "regular user" baseline | *pendiente* |
| SG_Workstation_Joiners | Security, Global | Delegated join-domain permission (planned for C3 — delegation, not yet done) | *pendiente* |

### Naming Conventions
- OUs: `<Department> → Users / Computers / Groups`
- Groups: `SG_<Department>_<Function>`

> [!info] Why this structure
> Departments chosen (IT / Security / Operations) instead of a generic business template map to real permission narratives relevant to a security career path — see [[Active Directory Design]] for full rationale.

---

## Change Log

### 2026-09-16 — C1: OU structure and security groups
**Changed:**
- Created `Departments` OU → IT / Security / Operations, each with Users/Computers/Groups sub-OUs
- Created `Service Accounts` OU at root (reserved for C2)
- Created groups: SG_IT_Admins, SG_IT_Users, SG_Security_Analysts, SG_Operations_Users, SG_Workstation_Joiners

**Verification lab:**
- [ ] Test user created inside each department's Users OU
- [ ] Confirmed correct OU placement in ADUC
- [ ] Moved a test user between OUs, confirmed update

**Issues:** 

---


