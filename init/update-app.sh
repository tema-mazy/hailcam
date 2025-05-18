#!/bin/bash
ip=$1

if [ -n "$ip" ]; then
    scp -r ../hailcam $ip:
    ssh $ip 'sudo systemctl restart cam'

else
   echo "Usage $0 <user@IP>"

fi