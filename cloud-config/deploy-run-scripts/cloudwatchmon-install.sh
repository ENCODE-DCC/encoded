#!/bin/bash
# Setup cloudwatchmon
# build user
# apt deps:
#       virtualenv
echo -e "\n**** ENCDINSTALL $(basename $0) ****"

DEPLOY_SCRIPT_DIR='/home/ubuntu/encoded/cloud-config/deploy-run-scripts'

CLOUDWATCHMON_HOME='/opt/cloudwatchmon'
CLOUDWATCHMON_REQS='cloudwatchmon-requirements.txt'
CLOUDWATCHMON_VENV="$CLOUDWATCHMON_HOME/.cwm-pyenv"

mkdir "$CLOUDWATCHMON_HOME"
cp "$DEPLOY_SCRIPT_DIR/$CLOUDWATCHMON_REQS" "$CLOUDWATCHMON_HOME/$CLOUDWATCHMON_REQS"
chown build:build "$CLOUDWATCHMON_HOME"
chown build:build "$CLOUDWATCHMON_HOME/$CLOUDWATCHMON_REQS"
sudo -H -u build python3 -m venv "$CLOUDWATCHMON_VENV"
sudo -H -u build "$CLOUDWATCHMON_VENV/bin/pip" --no-cache-dir install --upgrade pip setuptools
sudo -H -u build "$CLOUDWATCHMON_VENV/bin/pip" --no-cache-dir install -r "$CLOUDWATCHMON_HOME/$CLOUDWATCHMON_REQS"
