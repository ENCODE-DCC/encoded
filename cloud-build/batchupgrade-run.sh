#!/bin/bash
# Run batchupgrade
# encoded user
# apt deps:

env_ini=$1
sudo -i -u encoded bin/batchupgrade $env_ini --app-name app
