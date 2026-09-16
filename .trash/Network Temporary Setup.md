We will have to setup the IP of the networks with pfSense that will run on the A8 but we must first assign the correct IP addresses of the ports.

1 port will be connected to the router and the other to the switch which will connect the rest of the homelab.

A8 port 1 (Router): 192.168.0.10
A8 port 2 (Switch): 192.168.0.11
VAIO: 192.168.0.12


We will access the laptop through ssh and set it up from there. The first port has been already assigned an IP address in the OS installation so we would only need to assign the second port.

we will use this command to modify the interfaces and assign a static IP.
```
nano /etc/network/interfaces
```

![](attachments/Pasted%20image%2020260110161437.png)

