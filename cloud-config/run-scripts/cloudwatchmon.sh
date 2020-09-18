#!/bin/bash
# Setup cloudwatchmon
echo -e "$(basename $0) Running"

# Script Below
CLOUDWATCHMON_HOME='/opt/cloudwatchmon'
CLOUDWATCHMON_REQS='cloudwatchmon-pyreqs.txt'
CLOUDWATCHMON_VENV="$CLOUDWATCHMON_HOME/.cwm-pyenv"

sudo mkdir "$CLOUDWATCHMON_HOME"
sudo cp "$encd_cc_dir/run-scripts/$CLOUDWATCHMON_REQS" "$CLOUDWATCHMON_HOME/$CLOUDWATCHMON_REQS"
sudo chown build:build "$CLOUDWATCHMON_HOME"
sudo chown build:build "$CLOUDWATCHMON_HOME/$CLOUDWATCHMON_REQS"
sudo -H -u build "$encd_py3_env" -m venv "$CLOUDWATCHMON_VENV"
sudo -H -u build "$CLOUDWATCHMON_VENV/bin/pip" --no-cache-dir install --upgrade pip setuptools
sudo -H -u build "$CLOUDWATCHMON_VENV/bin/pip" --no-cache-dir install -r "$CLOUDWATCHMON_HOME/$CLOUDWATCHMON_REQS"
# Add to cron job
cron_line="*/5 * * * * nobody $CLOUDWATCHMON_VENV/bin/mon-put-instance-stats.py --mem-util --swap-util --disk-space-util --disk-path=/ --from-cron"
echo "$cron_line" | sudo -u root tee -a /etc/cron.d/cloudwatchmon
