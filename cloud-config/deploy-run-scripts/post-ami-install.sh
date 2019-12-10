#!/bin/bash

CC_DIR="$1"
ROLE="$2"
WALE_S3_PREFIX="$3"
PG_VERSION="$4"
GIT_REPO="$5"
GIT_REMOTE="$6"
GIT_BRANCH="$7"
ES_IP="$8"
ES_PORT="$9"
REGION_INDEX="$10"
APP_WORKERS="$11"
BUP_VAR_1="$12"
BUP_VAR_2="$13"
BUP_VAR_3="$14"
BUP_VAR_4="$15"

encoded_app_is_installed_file_flag='/home/ubuntu/.encoded_app_is_installed_file_flag'
encoded_app_do_install_file_flag='/home/ubuntu/.encoded_app_do_install_file_flag'
if [ -f "$encoded_app_is_installed_file_flag" ]; then
    echo 'POST AMI INSTALL: Installed Already'
else
    if [ -f "$encoded_app_do_install_file_flag" ]; then
        echo 'POST AMI INSTALL: Installing Now'
        sudo -u ubuntu git -C /home/ubuntu/encoded checkout -b $GIT_BRANCH $GIT_REMOTE/$GIT_BRANCH
        $CC_DIR/pg-install.sh off $ROLE $WALE_S3_PREFIX $PG_VERSION
        $CC_DIR/encd-install.sh $GIT_REPO $GIT_REMOTE $GIT_BRANCH $ROLE $ES_IP $ES_PORT $REGION_INDEX $APP_WORKERS
        $CC_DIR/a2en-run.sh
        if [ "$ROLE" == "demo" ]; then
          $CC_DIR/batchupgrade-run.sh production.ini $BUP_VAR_1 $BUP_VAR_2 $BUP_VAR_3 $BUP_VAR_4
        fi
        $CC_DIR/post-install-install.sh
        touch "$encoded_app_is_installed_file_flag"
    else
        echo 'POST AMI INSTALL: Setting do install'
        touch "$encoded_app_do_install_file_flag"
    fi
fi
