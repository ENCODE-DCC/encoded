#!/bin/bash
# Setup cloudwatchmon
# build user
# apt deps:
#       virtualenv
echo -e "\n**** ENCDINSTALL $(basename $0) ****"
DEPLOY_SCRIPT_DIR='cloud-config/deploy-run-scripts'
mkdir /opt/cloudwatchmon
chown build:build /opt/cloudwatchmon
cd /opt/cloudwatchmon
cp ~ubuntu/encoded/$DEPLOY_SCRIPT_DIR/cloudwatchmon-requirements.txt cloudwatchmon-requirements.txt
sudo -u build virtualenv --python=python2.7 ./
sudo -u build /opt/cloudwatchmon/bin/pip install -r cloudwatchmon-requirements.txt
