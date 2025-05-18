#!/bin/bash
mac=`ip a | grep link/ether | awk '{ print $2;}'| awk -F ':' '{ print $4$5$6;}'`
if [ -n "$mac" ]; then
    nmcli device wifi hotspot ssid "HailCam $mac" password "12345678"
    nmcli conn modify Hotspot connect.autoconnect-priority 200
    nmcli conn modify Hotspot connect.autoconnect yes
else
    echo "Can't determine MAC"
fi
