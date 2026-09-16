In this part of the project we will implement pfSense and design the infrastructure of the whole network. The point of this project is to have full control over my network and be able to improve the security of it.

# Target architecture

Our network fill follow this design

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

## Physical NIC assignment

|Proxmox NIC|Bridge|Purpose|
|---|---|---|
|NIC 1|`vmbr0`|WAN|
|NIC 2|`vmbr1`|LAN trunk|

pfSense VM:

```
WAN → vmbr0
LAN → vmbr1
```

Then `vmbr1` connects to the managed switch and carries the VLANs.

## Recommended VLAN plan

|VLAN|Name|Network|Purpose|
|---|---|---|---|
|10|HOME|`192.168.10.0/24`|Your personal devices|
|20|LAB-USERS|`10.10.10.0/24`|Windows clients|
|30|LAB-SERVERS|`10.10.20.0/24`|AD servers|
|40|LAB-ATTACKER|`10.10.40.0/24`|Kali|
|50|IOT|`192.168.50.0/24`|IoT devices|