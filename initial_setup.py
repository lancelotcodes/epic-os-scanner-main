import os, subprocess, time, setup_lib, sys


os.system('clear')
print()
print()
print("###################################")
print("######### BLE PIR Monitor #########")
print("######### Initial Setup   #########")
print("###################################")
print()
print()
setup_lib.install_prereqs()
setup_lib.copy_crontab()
os.system('clear')
os.system('reboot')