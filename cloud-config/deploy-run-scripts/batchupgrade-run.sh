#!/bin/bash
# Run batchupgrade
# encoded user
# apt deps:
echo -e "\n**** ENCDINSTALL $(basename $0) ****"
env_ini=$1
batchsize=$2
chunksize=$3
processes=$4
maxtasksperchild=$5
sudo -i -u encoded bin/batchupgrade $env_ini --app-name app --batchsize $batchsize --chunksize $chunksize --processes $processes --maxtasksperchild $maxtasksperchild
