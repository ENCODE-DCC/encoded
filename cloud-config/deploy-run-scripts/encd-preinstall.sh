#!/bin/bash
# Setup encoded app
# encoded user
# apt deps:
echo -e "\n**** ENCDINSTALL $(basename $0) ****"

GIT_REPO="$1"
GIT_REMOTE="$2"
GIT_BRANCH="$3"


git_uri="$GIT_REMOTE/$GIT_BRANCH"
encd_home='/srv/encoded'
mkdir "$encd_home"
chown encoded:encoded "$encd_home"
cd "$encd_home"
sudo -H -u encoded git clone "$GIT_REPO" "$encd_home"
sudo -H -u encoded git checkout -b "$GIT_BRANCH" "$git_uri"

encd_venv="$encd_home/.pyvenv"
sudo -H -u encoded python3 -m venv "$encd_venv"
source "$encd_venv/bin/activate"
sudo -H -u encoded "$encd_venv/bin/pip" install --upgrade pip setuptools
sudo -H -u encoded "$encd_venv/bin/pip" install --upgrade zc.buildout redis
