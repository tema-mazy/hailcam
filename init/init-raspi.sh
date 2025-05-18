#!/bin/bash
ip=$1

if [ -n "$ip" ]; then
    echo "Make shure you have generated ssh key"
    ssh-copy-id $ip
    echo "Init device"
    scp config.txt $ip:
    scp init-pri.sh $ip:
    ssh $ip "sudo /bin/bash ./init-pri.sh"
    echo "Init Cam App"
    scp -r ../hailcam $ip:
    ssh $ip 'cd hailcam && ./hc-init.sh'
    echo "Init Wifi AP"
    scp init-ap.sh $ip:
    ssh $ip "sudo /bin/bash ./init-ap.sh"
else
   echo "Usage $0 <user@IP>"
fi