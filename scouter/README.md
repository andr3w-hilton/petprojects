# Scouter

Scouter is the result of me trying to speed up and automate my hackthebox.eu initial scanning work-flow. I am very new to scripting/writing code so I thought it would be a good learning opportunity. 


At a high-level the script does the following:
1. Does the standard `nmap -sC -sV <target IP>` scan
2. Runs a masscan all tcp ports scan on non-default nmap tcp ports (~64535 ports)
3. If there are any results outside of the default nmap port range, the script will run a follow-up `nmap -sC -sV` scan on those ports
4. Runs a top 100 ports `nmap -sU --top-ports 100 <target IP>` scan
5. If there are any UDP ports discovered, the script will run a follow-up `nmap -sU -sC -sV` scan on those ports


## Details and Weird Discoveries


### Masscan is very naughty! 
Boy does masscan like to bug out over a VPN connection. I found that it regularly misses open UDP ports to the point that I could not rely on it. This problem persisted even if the scanning rate was decreased to 200 packets per second. 

I also found that masscan likes to hang. It will display a counter telling you when it plans on exiting and this counter will plunge into the -300 second range on occasion.

##### WTF?
The **weirdest** thing I discovered, was that if you run a UDP all-ports scan with masscan and simultaneously run an `nmap -sU` scan of any sort, the nmap results will be lightning quick. **This greatly reduces our scanning times**
