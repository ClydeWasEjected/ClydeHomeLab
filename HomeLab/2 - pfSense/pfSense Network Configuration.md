# pfSense Network Configuration

Related: [[pfSense Installation]] · [[pfSense Configuration]]

Initial interface/DHCP/DNS bring-up, done before the VLAN build. Current rules and VLANs live in [[pfSense Configuration]] — this doc is history only.

## What was done
- Enabled the LAN interface, assigned `10.10.10.1/24` (this is the network now called "Legacy LAN" in [Homelab - Inventory](<../1 - Infrastructure/Homelab - Inventory.md>)).
- Configured the DHCP server on LAN.
- Confirmed the network path: ISP router → pfSense → AP → home network; verified a client got a correct lease through the AP.

## ⚠️ Open security item — WAN GUI temporarily opened, closure not verified
While the laptop couldn't be physically connected to the LAN side yet, the web GUI was temporarily exposed on WAN via console shell:
```
pfSsh.php playback enableallowallwan
```
**No later note in any doc confirms this was reverted**, and [[pfSense Configuration]]'s current firewall rules only document LAN and per-VLAN rules — there's no WAN rule table at all. Check the live box (System > Advanced > Admin Access, and Firewall > Rules > WAN) to confirm the webConfigurator is not still reachable from WAN before trusting this is closed.

## Troubleshooting: DNS resolution
- Initial testing (ping `8.8.8.8` + DNS lookups) failed.
- Adding the LAN subnet to the DNS Resolver's access list did not fix it.
- Fixed by enabling **Forward Mode** on the DNS Resolver.

## Verification
![Fix applied — Forward Mode enabled on the DNS Resolver](attachments/Pasted%20image%2020260909012859.png)
![Confirmed working — DNS resolution succeeding after the fix](attachments/Pasted%20image%2020260909012917.png)
![Final network path confirmed — client got a correct IP through the AP and reached the internet](attachments/Pasted%20image%2020260909031957.png)
