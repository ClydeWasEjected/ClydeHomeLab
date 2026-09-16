# Objective
Deploy and simulate a basic enterprise Active Directory environment using Windows Server 2022 and Windows 11 clients for:

- Domain authentication
- DNS infrastructure
- Group Policy management
- Identity and access control testing
# Architecture
## Components
- DC01 (Windows Server 2022) → Domain Controller + DNS
- WIN11-01 (Windows 11 Enterprise) → Domain Client
- Proxmox Host → Virtualization platform
# Network Configuration  

| Device   | IP Address    | DNS         | Role              |     |
| -------- | ------------- | ----------- | ----------------- | --- |
| DC01     | 10.10.20.21   | 10.10.20.1  | Domain Controller |     |
| WIN11-01 | DHCP / Static | 10.10.20.21 | Client            |     |
## DNS Rules (Critical)
- All domain machines MUST use DC01 as DNS
- DC01 resolves:
    - Active Directory records
    - Internal domain (`studentboard.local`)
- External resolution handled via DNS forwarders
## Domain Configuration  
- Domain: jnclydehl.local  
- NetBIOS: JNCLYDEHL
- Forest Type: Single Domain Forest  
- Functional Level: Windows Server 2022

# Proxmox Virtualization Setup
## Host Configuration
- Hypervisor: Proxmox VE
- Bridge: `vmbr0` (bridged network)
- Storage: local-lvm
- ISO storage: local
## Vm Specifications
### Create DC01
- Windows Server 2022
- 2 CPU
- 4GB RAM
- 50GB Disk
- Network: vmbr0
### Create Win11-01
- Windows 11 Enterprise
- 2 CPU
- 4GB RAM
- 60GB disk

![](attachments/Pasted%20image%2020260531005219.png)

