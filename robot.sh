#!/usr/bin/bash
fuser -k 8000/tcp
fuser -k 3000/tcp
#sudo nmcli con up Hotspot
cd /home/pi/dyplom/build
(trap 'kill 0' SIGINT; python -m http.server 3000 & cd ..; ./motor.py)
