# Scouter

Scouter is the result of me trying to speed up and automate my hackthebox.eu initial scanning work-flow. I am very new to scripting/writing code so I thought it would be a good learning opportunity. **Please keep in mind that it is optimized specifically for the hackthebox VPN environment.** If you want to know more about the quirks associated with scanning in the hackthebox VPN I discovered, read the Details section below. When a box drops, you could get a couple minutes ahead of the crowd

At a high-level the script does the following:
1. Does the standard `nmap -sC -sV <target IP>` scan
2. Runs a masscan all tcp ports scan on non-default nmap tcp ports (~64535 ports)
3. If there are any results outside of the default nmap port range, the script will run a follow-up `nmap -sC -sV` scan on those ports
4. Runs a top 100 ports `nmap -sU --top-ports 100 <target IP>` scan
5. If there are any UDP ports discovered, the script will run a follow-up `nmap -sU -sC -sV` scan on those ports


## Details and Weird Discoveries

### Masscan is very naughty! 
Boy does masscan like to bug out over a VPN connection. I found that it regularly misses open UDP ports to the point that I could not rely on it. This problem persisted even if the scanning rate was decreased to 200 packets per second. 

I also found that masscan likes to hang. It will display a counter telling you when it plans on exiting and this counter will plunge into the -300 second range on occasion. To mitigate this potential danger, I put a function in the script called 'cop' which will run for a little over 2 minutes and then issue a `pkill -f masscan` command.

###### WTF?
The **weirdest** thing I discovered, was that if you run a UDP all-ports scan with masscan and simultaneously run an `nmap -sU` scan of any sort, the nmap results will be lightning quick. **This greatly reduces our scanning times.** To take advantage of this potential boost, I added a function called 'turbo' which will run a `masscan -pU:1-65535 -e tun0 --rate=200 <target IP>` scan and direct both stderr and stdout to /dev/null since we don't need the output (remember, it doesn't catch open ports). All we need it to do is run to get our nmap turbo boost.

The script could be easily altered to take advantage of a better masscan if used outside of the hackthebox environment. Have fun altering it to suit your needs.

### Hardcoded Bash Commands
I used a lot of hardcoded bash commands in the script so I could learn more about bash utilities such as awk, cut, sed, head, tr, etc. I'm sure the string slicing methods available in Python could be leveraged to change the output as well, I just preferred to learn some bash commands. If you're not a fan of the hardcoded commands or the output format, change it up!

### Multi-Processing
The script takes advantage of multi-processing by running a bunch of the commands simultaenously, this greatly reduces the scanning time. My original script, which performed all the commands in a linear fashion finished a test box in ~6 minutes, while this multi-processing version finished the same box in ~2 minutes flat. 

### Argument Parsing
This is the part I'm most ashamed of, the CLI-argument parsing seems very clumsy haha. Feel free to tell me how to do it better. I'm very new to this. 

HMU on twitter @h0mbre_ if you get anything out of it! 




