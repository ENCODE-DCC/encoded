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

# Create venv
sudo -H -u encoded "$ENCD_PY3_PATH" -m venv "${ENCD_VENV_DIR}"

# Update pip
source "${ENCD_VENV_DIR}/bin/activate"
sudo -H -u encoded "$(which pip)" install --upgrade pip==20.2.4
if [ $? -gt 0 ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: could not upgrade pip"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
