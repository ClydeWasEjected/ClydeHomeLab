# Objective
The objective of this setup is to enable secure remote access to the Proxmox hypervisor using Tailscale. This allows the homelab to be managed from outside the local network without exposing any services directly to the internet.

---
## Overview
Tailscale is installed directly on the Proxmox host in order to create a private VPN overlay network. Once connected, the Proxmox interface becomes accessible through a private Tailscale IP, making it possible to manage virtual machines, storage, and system configuration remotely.

This approach keeps the lab secure because no ports need to be forwarded on the router and no services are exposed publicly.

---
# Installation

Tailscale is installed on Proxmox using the official installation script provided by Tailscale. This script automatically configures the required repositories and installs the service.

```bash
curl -fsSL https://tailscale.com/install.sh | sh
````

---

## Service Activation

After installation, the Tailscale service must be enabled and started so it runs continuously in the background. This ensures the VPN connection persists even after system reboots.

```bash
systemctl enable tailscaled
systemctl start tailscaled
```

---

## Authentication

To connect the Proxmox host to the Tailscale network, the following command is executed:

```bash
tailscale up
```

After running this command, a login URL is generated. This URL is opened in a browser and used to authenticate the device under a Tailscale account. Once authenticated, the Proxmox host becomes part of the private Tailscale network.

---

## Verification

To confirm that the connection is active and functioning correctly, the following commands are used.

The first command checks the overall status of the Tailscale network and shows all connected devices:

```bash
tailscale status
```

The second command retrieves the private Tailscale IP assigned to the Proxmox host:

```bash
tailscale ip -4
```

The expected output is an IP address in the `100.x.x.x` range, which is the internal address used for secure remote access.

---

## Access

Once the setup is complete, Proxmox can be accessed remotely using the assigned Tailscale IP address. The web interface remains unchanged; only the access method is different.

[https://100.x.x.x:8006](https://100.x.x.x:8006/)

This replaces the local network access address:

[https://192.168.0.20:8006](https://192.168.0.20:8006/)

---

## Why Tailscale is installed only on Proxmox (for this stage)

At this stage of the homelab, installing Tailscale only on the Proxmox host is sufficient because Proxmox already provides full control over all virtual machines. Through the Proxmox dashboard, it is possible to start, stop, and manage all VMs, as well as access their console directly.

This means there is no immediate requirement to install Tailscale inside each individual VM.

---

## When per-device Tailscale becomes useful

Installing Tailscale inside individual virtual machines such as DC01 or Windows 11 clients becomes useful in more advanced scenarios. This allows direct access to each machine independently without going through the Proxmox interface. It is useful for simulating real enterprise environments where each endpoint is independently reachable.

It is also relevant for security testing, segmentation experiments, and situations where Proxmox is unavailable but individual machines still need access.

---
