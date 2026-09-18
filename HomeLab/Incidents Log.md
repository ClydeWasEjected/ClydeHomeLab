---
sticker: emoji//1f534
color: var(--mk-color-red)
---
> One section per incident. Newest on top. Each entry: Symptom → Root cause → Fix → Verification → Follow-up. This is the narrative/investigation record — the _current_ state of any system stays in its own reference doc (e.g. [[pfSense Configuration]], [Homelab - Inventory](1%20-%20Infrastructure/Homelab%20-%20Inventory.md)); update those separately if an incident changed something permanently.

## 2026-09-16 — LAN gateway auto-selected as default, breaking WAN routing

**Affected:** pfSense · [[pfSense Configuration]]

- **Symptom:** LAN clients got valid DHCP leases and could reach the pfSense GUI, but had no internet access. WAN gateway (`WAN_DHCP`) showed "pending" in Status > Gateways.
- **Root cause:** No IPv4 default gateway was explicitly pinned in System > Routing > Gateways. pfSense's automatic gateway-selection logic defaulted to LAN's gateway (`LANGW`) instead of WAN on every boot/reload — confirmed recurring across multiple reboots in system logs predating this session.
- **Contributing/secondary issue:** During interface reassignment via console (20:13), `dhcpd` briefly failed to bind to LAN ("no subnet declaration for vtnet1") — transient, self-resolved by the next filter reload once the interface's IP was consistently applied.
- **Fix:** System > Routing > Gateways > edit `WAN_DHCP` > check "Default Gateway" (IPv4) > save.
- **Verification:** Status > Gateways shows `WAN_DHCP` online (default); phone regained internet access.
- **Follow-up:** NTP fails to sync (config syntax error in `ntpd` startup, every boot) — clock reliability affects log timestamp accuracy; needs separate fix. _(open)_

### Aftermath

- **DHCP Static Mapping:** static mapping conflicted because the main laptop's IP was already taken by a different device — changed from `10.10.10.8` to `10.10.10.23`. _(→ update [Homelab - Inventory](1%20-%20Infrastructure/Homelab%20-%20Inventory.md) main PC row)_
- **Firewall Proxmox rule:** source address updated to match the main laptop's new IP after the change above.