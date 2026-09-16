After the installation we will proceed by configuring pfSense to follow our network plan.

# Interfaces
Before starting to add a DHCP server we will have to check on your interfaces first.

![](attachments/Pasted%20image%2020260908163717.png)

In our LAN interface we must enable it and add our subnet which is `10.10.10.1/24`
![](attachments/Pasted%20image%2020260908163810.png)

# WAN GUI (Temporary)

Since I can't connect physically my laptop to the server I will temporarily open the GUI to the WAN network to be able to access it.

To do so we access to the `SHELL` by selecting the option 8 and using these commands:

```
pfSsh.php playback enableallowallwan
```

![](attachments/Pasted%20image%2020260908231459.png)

![](attachments/Pasted%20image%2020260908232139.png)
# DHCP Server

After configuring our interfaces we will start with our DHCP server to assign IP addresses to our clients.

![](attachments/Pasted%20image%2020260909010439.png)

# Testing Network

After setting up the DHCP, I started to test if I can ping google and the DNS.

At first I had some issues with the DNS and I have tried multiple troubleshooting and configurations.

![](attachments/Pasted%20image%2020260909010925.png)

I added the Subnet to the Access list to see if that fixed it and it didn't.

![](attachments/Pasted%20image%2020260909011721.png)

By enabling Forward Mode it has worked and now DNS works correctly.

![](attachments/Pasted%20image%2020260909012859.png)![](attachments/Pasted%20image%2020260909012917.png)

# Setting Up Network Architecture

The plan is to use the ISP router to feed network to the server and use my personal router as an AP.

To do so we must configure the cabling by the following order:

ISP Router --> pfSense --> AP --> Home network

Now by connecting my laptop to my AP I see that it receives the correct IP address and I can connect to the network correctly.

![](attachments/Pasted%20image%2020260909031957.png)