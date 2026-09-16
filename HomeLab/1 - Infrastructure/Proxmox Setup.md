Before anything we must first set up proxmox so we can start running virtual machines. We will be using [NetworkChuck](https://www.youtube.com/watch?v=_u8qTN3cCnQ)'s video to guide the set up of Proxmox.

## Objectives
Prepare Proxmox to deploy a virtualization that will host:

- Windows Server 2022 (Active Directory)
- Windows 11 Enterprise Clients
- Entra ID and Intune testing environments
- Exchange and Autopilot lab systems
- Future cybersecurity and infrastructure projects

---
## Access URL

To access Proxmox:
https://192.168.0.20:8006/

---
# Setting Up Storage

In this part we will increase the storage that will allow us to use.

We can see a "local-lvm", we will not be using that and won't be needed. We can also see a "local" which will be the usable storage.

![](attachments/Pasted%20image%2020260531000234.png)

We will be deleting "local-lvm" since we don't need it and will allocate the space to "local".

![](attachments/Pasted%20image%2020260531000519.png)

After removing it, we will use the shell from the node.

We will use:
`lvremove /dev/pve/data`

![](attachments/Pasted%20image%2020260531000904.png)

Then resize storage:
`lvresize -l +100%FREE /dev/pve/root`

![](attachments/Pasted%20image%2020260531001120.png)

Confirm resize:
`resize2fs /dev/mapper/pve-root`

![](attachments/Pasted%20image%2020260531001332.png)

Now "local" has full storage available.

![](attachments/Pasted%20image%2020260531001406.png)

---

# Verify Network

Before proceeding let's verify the node's network.

![](attachments/Pasted%20image%2020260531001604.png)

We can see that the interface needed is active.

We will proceed by pinging 8.8.8.8 and test DNS.

![](attachments/Pasted%20image%2020260531001712.png)

---

## Network Configuration (Proxmox)

- Physical NIC: enx............ (NO IP assigned)
- Bridge: vmbr0
- Management IP: 192.168.0.20/24
- Gateway: 192.168.0.1

All VMs use vmbr0 for network access.

---

# Issues Encountered

---

## 1. KVM Virtualization Not Available

- Issue: VM failed to start with "KVM virtualisation configured, but not available"
- Cause: AMD SVM was not enabled in BIOS
- Fix:
  - Entered BIOS
  - Enabled SVM (AMD Virtualization)
  - Fully powered off system (cold boot)
  - Verified KVM module loaded successfully
- Result: Hardware virtualization became available

---

## 2. Invalid VM Network Bridge Configuration

- Issue: VM failed to start with "bridge is neither a linux nor an OVS bridge"
- Cause: VM attached to physical NIC instead of vmbr0
- Fix:
  - Created/validated vmbr0 bridge in Proxmox
  - Moved VM network adapter to vmbr0
- Result: VM networking restored

---

# Network Design

## Current Lab Network

This is the current working network used for all Proxmox and virtual machines.

- Proxmox Host: 192.168.0.20
- DC01: 192.168.0.21
- WIN11-01: 192.168.0.22 (planned)
- Router: 192.168.0.1
- Network: 192.168.0.0/24

---

## Design Rules

- All virtual machines are in the same LAN subnet (192.168.0.0/24)
- Proxmox uses vmbr0 for all networking
- Each VM must have a unique static IP
- No IP conflicts are allowed

---

# Conclusion

Proxmox has been successfully configured as a virtualization platform. Storage has been optimized, and network connectivity has been validated. The environment is now ready for Active Directory deployment using Windows Server 2022 and Windows 11 clients.