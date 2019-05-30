#!/bin/bash
# Setup cloudwatchmon
# build user
# apt deps:
#       virtualenv


mkdir /opt/cloudwatchmon
chown build:build /opt/cloudwatchmon
cd /opt/cloudwatchmon
cp ~ubuntu/encoded/cloudwatchmon-requirements.txt cloudwatchmon-requirements.txt
sudo -u build virtualenv --python=python2.7 ./
sudo -u build /opt/cloudwatchmon/bin/pip install -r cloudwatchmon-requirements.txt
