#!/bin/bash
# Run batchupgrade
echo -e "$(basename $0) Running"

env_ini=$1
batchsize=$2
chunksize=$3
processes=$4
maxtasksperchild=$5
args_str="$env_ini --app-name app --batchsize $batchsize --chunksize $chunksize --processes $processes --maxtasksperchild $maxtasksperchild"
echo -e "$(basename $0) $args_str"
cd "$encd_home"
sudo -i -u encoded bin/batchupgrade $env_ini --app-name app --batchsize $batchsize --chunksize $chunksize --processes $processes --maxtasksperchild $maxtasksperchild
if [ $? -gt 0 ]; then
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
