#!/bin/bash
cp config.txt /boot/firmware
for m in g_serial i2c_dev; do
    if [ -z `cat /etc/modules | grep $m` ]; then
	modprobe $m
        echo "$m" >> /etc/modules
    fi
done

sudo systemctl enable serial-getty@ttyGS0.service
sudo systemctl start serial-getty@ttyGS0.service

sed -i 's/^AcceptEnv LANG/#AcceptEnv LANG/i' /etc/ssh/sshd_config

cat << EOF > /etc/NetworkManager/dispatcher.d/nm-connect.sh 
#!/bin/bash
iface="\$1"
state="\$2"

# BLUE LED on GPIO11
gpio=11

if [[ "\$state" == "up" ]]; then
   /usr/bin/gpioset gpiochip0 \$gpio=1
elif [[ "\$state" == "down" ]]; then
   /usr/bin/gpioset gpiochip0 \$gpio=0
fi
EOF

chmod +x /etc/NetworkManager/dispatcher.d/nm-connect.sh 



cat << EOF > /etc/systemd/system/cam.service
[Unit]
Description=HailCam
After=network.target

[Service]
TimeoutStartSec=30
TimeoutStopSec=5
Restart=always

EnvironmentFile=-/etc/default/hailcam

WorkingDirectory=/home/pi/hailcam
ReadWriteDirectories=/home/pi/hailcam
PrivateTmp=true
User=pi
Group=pi
ExecStart=/home/pi/hailcam/.env/bin/python3 /home/pi/hailcam/hailcam.py

StandardError=journal

SyslogIdentifier=hailcam


[Install]
WantedBy=multi-user.target
EOF
systemctl enable cam

DEBIAN_FRONTEND=noninteractive apt -y update && apt -y upgrade
DEBIAN_FRONTEND=noninteractive apt -y install mc libcap-dev libgl1 python3-dev python3-libcamera python3-kms++ python3-smbus

