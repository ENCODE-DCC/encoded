#!/bin/bash
# Run batchupgrade
echo -e "\n$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
env_ini=$1
batchsize=$2
chunksize=$3
processes=$4
maxtasksperchild=$5
args_str="$env_ini --app-name app --batchsize $batchsize --chunksize $chunksize --processes $processes --maxtasksperchild $maxtasksperchild"
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) $args_str"
cd "$ENCD_HOME"
source "${ENCD_VENV_DIR}/bin/activate"
sudo -i -u encoded "$(which batchupgrade)" $env_ini --app-name app --batchsize $batchsize --chunksize $chunksize --processes $processes --maxtasksperchild $maxtasksperchild
if [ $? -gt 0 ]; then
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
