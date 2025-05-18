#!/bin/bash
python3 -m venv --system-site-packages --upgrade .env
.env/bin/pip3 install --ignore-installed -r mock-req.txt 
