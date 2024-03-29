#!/bin/bash
# Setup encoded app
echo -e "\n$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Running"

# Install App
cd "$ENCD_HOME"
source "${ENCD_VENV_DIR}/bin/activate"
pip_install_cmd="$(which pip) install -e ."
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) CMD: $pip_install_cmd"
sudo -H -u encoded $pip_install_cmd
if [ $? -gt 0 ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: pip return error status"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi

# Copy correct conf file to repo root
sudo -u encoded cp "conf/pyramid/${ENCD_PYRAMID_CONFIG_NAME}.ini" production.ini

# Install snovault editably if specified in deploy
if [ "$ENCD_DEVELOP_SNOVAULT" == 'true' ]; then
    source "${ENCD_VENV_DIR}/bin/activate"
    SNOVAULT_DEP=$(grep "SNOVAULT_DEP =" setup.py | cut -d "=" -f 2 | tr -d '" ')
    PIP_INSTALL_CMD="$(which pip) install -e ${SNOVAULT_DEP}#egg=snovault --src /srv/encoded"
    sudo -H -u encoded ${PIP_INSTALL_CMD}
    if [ $? -gt 0 ]; then
        echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: pip return error status"
        # Build has failed
        touch "$encd_failed_flag"
        exit 1
    fi
fi

# Install JS dependencies and build
make_cmd="make javascript-and-download-files"
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) CMD: $make_cmd"
sudo -H -u encoded $make_cmd
if [ $? -gt 0 ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: make return error status"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi

some_other_bin_path="$(which batchupgrade)"
if [ ! -f "$some_other_bin_path" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: bin commands do not exist"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi

# Downlaod encoded demo aws keys
encd_keys_dir=/home/ubuntu/encd-aws-keys
mkdir "$encd_keys_dir"
aws s3 cp --region=us-west-2 --recursive s3://encoded-conf-prod/encd-aws-keys "$encd_keys_dir"
if [ ! -f "$encd_keys_dir/credentials" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: ubuntu home encd aws creds"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi

# Add aws keys to encoded user
sudo -u encoded mkdir /srv/encoded/.aws
sudo -u root cp /home/ubuntu/encd-aws-keys/* /srv/encoded/.aws/
sudo -u root chown -R encoded:encoded ~encoded/.aws

# Add ssh keys to encoded user
sudo -u encoded mkdir /srv/encoded/.ssh
sudo -u root cp /home/ubuntu/.ssh/authorized_keys /srv/encoded/.ssh/authorized_keys
sudo -u root chown -R encoded:encoded /srv/encoded/.ssh/authorized_keys

## Wait for psql to come up
$ENCD_SCRIPTS_DIR/app-pg-status.sh
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: App pg status"
    exit 1
fi

# Finished running post pg scripts
sudo -H -u encoded sh -c 'cat /dev/urandom | head -c 256 | base64 > session-secret.b64'
if [ ! "$ENCD_BUILD_TYPE" == 'app' ]; then
    sudo -H -u encoded "$(which create-mapping)" "$ENCD_HOME/production.ini" --app-name app
    if [ $? -gt 0 ]; then
        echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: create-mapping return error status"
        # Build has failed
        touch "$encd_failed_flag"
        exit 1
    fi
fi

sudo -u root cp /srv/encoded/etc/logging-apache.conf /etc/apache2/conf-available/logging.conf

# Create encoded apache conf
sudo -u root "$ENCD_HOME/cloud-config/configs/apache/build-conf.sh"
