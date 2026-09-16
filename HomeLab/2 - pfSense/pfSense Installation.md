We will start by creating the VM in pfSense and add the following configurations:

```
RAM: 32 GB
CPU:2 cores
Memory:4096 MB
```

![](attachments/Pasted%20image%2020260908144229.png)

## Network Interfaces

Create **two network devices**.

 Network Device 1 — WAN
```
Bridge: vmbr0
Model: VirtIO (paravirtualized)
```
 
 Network Device 2 — LAN
```
Bridge: vmbr1
Model: VirtIO (paravirtualized)
```

```
pfSense
│
├── net0 → vmbr0 → WAN_NIC → ISP router
│
└── net1 → vmbr1 → LAN_NIC → Managed Switch
```

### Creating vmbr1

![](attachments/Pasted%20image%2020260908144556.png)

At this point we need to connect the server to the swithc

# Booting up pfSense

After the configuration I started by setting up pfSense, The installation it's just the basic steps of an OS installation besides some networking parts.

![](attachments/Pasted%20image%2020260908150912.png)

After all of this is just all next.

After the installation it should be done and ready to set up

![](attachments/Pasted%20image%2020260908155036.png)

As we can see it has assigned us an IP to access the dashboard.

![](attachments/Pasted%20image%2020260908155146.png)

# pfSense Setup Wizard

It will ask us for the basic configuration to fill out:

![](attachments/Pasted%20image%2020260908155504.png)

![](attachments/Pasted%20image%2020260908155531.png)

In this part I will just leave it as default.![](attachments/Pasted%20image%2020260908155737.png)

And then it will ask us to change the admin password.
![](attachments/Pasted%20image%2020260908155827.png)

After all this we got pfSense ready.

![](attachments/Pasted%20image%2020260908155943.png)