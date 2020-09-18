#!/bin/bash
# Setup encoded app environment
echo -e "\n$(basename $0) Running"

standby_mode='off'

# Script Below
# Create encoded user home
sudo mkdir "$encd_home"
sudo chown encoded:encoded "$encd_home"

sudo cp -r ~ubuntu/.ssh "$encd_home/.ssh"
sudo chown -R encoded:encoded "$encd_home/.ssh"

# Checkout encoded repo
cd "$encd_home"
sudo -H -u encoded git init
sudo -H -u encoded git remote add origin "$encd_git_repo"
sudo -H -u encoded git pull
sudo -H -u encoded git checkout -b "$encd_git_branch" "$encd_git_remote/$encd_git_branch"

# Create pyenv
encd_venv="$encd_home/.pyvenv"
sudo -H -u encoded "$encd_py3_env" -m venv "$encd_venv"

# Install pre-reqs
source "$encd_venv/bin/activate"
sudo -H -u encoded "$encd_venv/bin/pip" install --upgrade pip setuptools
sudo -H -u encoded "$encd_venv/bin/pip" install -r requirements.txt

cd "$encd_cc_dir/run-scripts"
./java.sh
./elasticsearch.sh
./wait-es-status.sh
./postgres.sh
./wait-pg-status.sh
