#!/bin/bash
mac=`ip a | grep link/ether | awk '{ print $2;}'| awk -F ':' '{ print $4$5$6;}'`
if [ -n "$mac" ]; then
    nmcli device wifi hotspot ssid "HailCam AP $mac" password "12345678"
else
    echo "Can't determine MAC"
fi
