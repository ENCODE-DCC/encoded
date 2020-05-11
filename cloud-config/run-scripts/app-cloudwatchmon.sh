#!/bin/bash
# Setup cloudwatchmon
echo -e "\n$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
if [ ! -f "$encd_is_installed_flag" ]; then
    # Cloudwatch only needs to be installed on non ami builds, after app is installed
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping for AMI build"
    exit 0
else
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Running"
fi

# Script Below
CLOUDWATCHMON_HOME='/opt/cloudwatchmon'
CLOUDWATCHMON_REQS='app-cloudwatchmon-pyreqs.txt'
CLOUDWATCHMON_VENV="$CLOUDWATCHMON_HOME/.cwm-pyenv"

sudo mkdir "$CLOUDWATCHMON_HOME"
sudo cp "$ENCD_SCRIPTS_DIR/$CLOUDWATCHMON_REQS" "$CLOUDWATCHMON_HOME/$CLOUDWATCHMON_REQS"
sudo chown build:build "$CLOUDWATCHMON_HOME"
sudo chown build:build "$CLOUDWATCHMON_HOME/$CLOUDWATCHMON_REQS"
sudo -H -u build "$ENCD_PY3_PATH" -m venv "$CLOUDWATCHMON_VENV"
sudo -H -u build "$CLOUDWATCHMON_VENV/bin/pip" --no-cache-dir install --upgrade pip setuptools
sudo -H -u build "$CLOUDWATCHMON_VENV/bin/pip" --no-cache-dir install -r "$CLOUDWATCHMON_HOME/$CLOUDWATCHMON_REQS"
# Add to cron job
cron_line="*/5 * * * * nobody $CLOUDWATCHMON_VENV/bin/mon-put-instance-stats.py --mem-util --swap-util --disk-space-util --disk-path=/ --from-cron"
echo "$cron_line" | sudo -u root tee -a /etc/cron.d/cloudwatchmon
