#!/bin/bash
# Run batchupgrade
# encoded user
# apt deps:

env_ini=$1
batchsize=$2
processes=$3
sudo -i -u encoded bin/batchupgrade $env_ini --app-name app --batchsize $batchsize --processes $processes
