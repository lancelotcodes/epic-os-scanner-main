#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home

cd /

sleep 5

bluetoothctl << EOF
power on
default-agent
EOF

sleep 10

cd /
cd /home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/src
sudo python3 main.py
cd /