#!/bin/bash
# Setup encoded app environment
echo -e "\n$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
# Create encoded user home
sudo mkdir "$ENCD_HOME"
sudo chown encoded:encoded "$ENCD_HOME"

# Checkout encoded repo
cd "$ENCD_HOME"
sudo -H -u encoded git clone "$ENCD_GIT_REPO" "$ENCD_HOME"
sudo -H -u encoded git checkout -b "$ENCD_GIT_BRANCH" "$ENCD_GIT_REMOTE/$ENCD_GIT_BRANCH"

# Create pyenv
encd_venv="$ENCD_HOME/.pyvenv"
sudo -H -u encoded "$ENCD_PY3_PATH" -m venv "$encd_venv"

# Install pre-reqs
source "$encd_venv/bin/activate"
sudo -H -u encoded "$encd_venv/bin/pip" install --upgrade pip setuptools
sudo -H -u encoded "$encd_venv/bin/pip" install -r requirements.txt
if [ $? -gt 0 ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: Penv install failed"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
