#!/bin/bash
# Install encoded application on deploying with base ami
echo -e "\n$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
BUP_VAR_1="${1}"
BUP_VAR_2="${2}"
BUP_VAR_3="${3}"
BUP_VAR_4="${4}"
ROLE="${5}"

standby_mode='off'
if [ "$ENCD_ROLE" == 'candidate' ]; then
    standby_mode='on'
fi

encoded_app_is_installed_file_flag='/home/ubuntu/.encoded_app_is_installed_file_flag'

function fix_repo {
    repo_dir="$1"
    repo_remote="$2"
    branch_name="$3"
    user="$4"
    cd "$repo_dir"
    sudo -H -u "$user" git stash
    sudo -H -u "$user" git branch -m original-branch
    sudo -H -u "$user" git checkout original-branch
    sudo -H -u "$user" git fetch origin --prune
    sudo -H -u "$user" git checkout -b "$branch_name" "$repo_remote/$branch_name"
    sudo -H -u "$user" git checkout "$branch_name"
}


# Deploy flag to build without base ami
if [ $ENCD_FULL_BUILD == 'True' ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD_FULL_BUILD=$ENCD_FULL_BUILD"
    touch "$encd_do_install_flag"
fi

# Base ami deployment.  Do not install application, but set flag to do so next time
if [ ! -f "$encd_do_install_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) POST AMI INSTALL: Set Do Install Flag"
    touch "$encd_do_install_flag"
    exit 0
fi

# Application is already install.  May never run?
if [ -f "$encd_is_installed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) POST AMI INSTALL: Is Installed"
    touch "$encd_is_installed_flag"
    exit 0
fi

# Install application
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) POST AMI INSTALL: Do Install"

# Set echo string to be used in app wrapper sub scripts
export APP_WRAPPER="(app-wrapper)\t"

# Update repos encoded and ubuntu
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Fix ubuntu branch"
fix_repo '/home/ubuntu/encoded' "$ENCD_GIT_REMOTE" "$ENCD_GIT_BRANCH" "ubuntu"
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Fix encoded branch"
fix_repo "$ENCD_HOME" "$ENCD_GIT_REMOTE" "$ENCD_GIT_BRANCH" "encoded"

# Run app install scripts
$ENCD_SCRIPTS_DIR/app-es-status.sh
if [ -z "$ENCD_PG_IP" ]; then
    $ENCD_SCRIPTS_DIR/app-pg.sh "$standby_mode"
fi
$ENCD_SCRIPTS_DIR/app-encd.sh
sudo -u root $ENCD_SCRIPTS_DIR/app-a2en.sh
if [ "$ENCD_BATCHUPGRADE" == "true" ]; then
    sleep 1m
    $ENCD_SCRIPTS_DIR/app-batchupgrade.sh production.ini $BUP_VAR_1 $BUP_VAR_2 $BUP_VAR_3 $BUP_VAR_4
fi
$ENCD_SCRIPTS_DIR/app-final.sh

# Set flag, eventhough the install could have failed
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) POST AMI INSTALL: Set Is Installed Flag"
touch "$encd_is_installed_flag"
export APP_WRAPPER=""
