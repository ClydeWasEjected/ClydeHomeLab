# pfSense Design

## 1. Purpose

pfSense provides routing, firewalling, DHCP, DNS, and network segmentation for the room network and cybersecurity homelab.

pfSense runs as a virtual machine on the Proxmox hypervisor.

The pfSense instance is the primary router and firewall for the network behind the Proxmox host.

## Target architecture

Our network fill follow this design
```

               ISP / existing router
                         │
                         │
                  enx00e04c4d6938
                         │
                       vmbr0
                         │
                    pfSense WAN
                         │
                    pfSense VM
                         │
                    pfSense LAN
                         │
                       nic0
                         │
                  Managed Switch
                         │
              ┌──────────┼──────────┐
              │          │          │
            HOME        LAB       ATTACKER
```
## 2. Virtualization

|Component|Configuration|
|---|---|
|Hypervisor|Proxmox VE|
|VM|pfsense-01|
|CPU|2 cores|
|RAM|4 GB|
|Storage|20 GB|
|WAN|vmbr0|
|LAN|vmbr1|

## 3. Physical Interfaces

| Interface | Type              | Proxmox Role |
| --------- | ----------------- | ------------ |
| WAN_NIC   | USB Ethernet      | WAN          |
| LAN_NIC   | Physical Ethernet | LAN          |

## 4. Proxmox Bridges

### vmbr0 — WAN

```text
enx00e04c4d6938
        │
      vmbr0
        │
   pfSense WAN
```

The existing Proxmox management network currently uses this bridge.

```Example Proxmox management address: 
192.168.0.20/24 

Example gateway: 
192.168.0.1
```

### vmbr1 — LAN

```text
nic0
 │
vmbr1
 │
pfSense LAN
 │
Managed Switch
```

This bridge will provide pfSense with access to the internal room network.

## 5. Network Segmentation

The internal network will be divided into separate security zones using VLANs.

|VLAN|Name|Subnet|Purpose|
|---|---|---|---|
|10|HOME|192.168.10.0/24|Personal devices|
|20|LAB-USERS|10.10.10.0/24|Windows clients|
|30|LAB-SERVERS|10.10.20.0/24|Servers / Active Directory|
|40|ATTACKER|10.10.40.0/24|Security testing|
|50|IOT|192.168.50.0/24|IoT devices|

## 6. Security Objective

The home network and cybersecurity lab must remain logically separated.

The ATTACKER network is intentionally isolated from the HOME network.

Firewall rules will control communication between VLANs.

The default security posture will be deny-by-default, with only required traffic explicitly permitted.