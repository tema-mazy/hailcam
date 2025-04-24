#!/bin/bash
apt -y install libcap-dev python3-libcamera python3-kms++ python3-smbus
python3 -m venv --system-site-packages --upgrade .env
.env/bin/pip3 install --ignore-installed -r req.txt 
