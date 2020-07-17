#!/bin/bash
# Setup encoded app
echo -e "\n$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below

# Check remote postgres uri
PG_URI='postgresql:///encoded'
if [ "$ENCD_BUILD_TYPE" == 'app' ] || [ "$ENCD_BUILD_TYPE" == 'app-es' ]; then
    PG_URI="postgresql://$ENCD_PG_IP/encoded"
fi
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD PG_URI: $PG_URI"

# Install App
cd "$ENCD_HOME"

# Run bootstrap
sudo -H -u encoded "$ENCD_HOME/.pyvenv/bin/buildout" bootstrap
bin_build_path="$ENCD_HOME/bin/buildout"
if [ $? -gt 0 ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: bootstrap return error status"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
if [ ! -f "$bin_build_path" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: Bootstrap"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi

# Run bin/buildout
bin_build_cmd="$ENCD_HOME/bin/buildout -c $ENCD_ROLE.cfg buildout:es-ip=$ENCD_ES_IP buildout:es-port=$ENCD_ES_PORT buildout:pg-uri=$PG_URI buildout:fe-ip=$ENCD_FE_IP buildout:remote_indexing=$ENCD_REMOTE_INDEXING buildout:index_procs=$ENCD_INDEX_PROCS buildout:index_chunk_size=$ENCD_INDEX_CHUNK_SIZE"
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) CMD: $bin_build_cmd"
sudo -H -u encoded LANG=en_US.UTF-8 $bin_build_cmd
if [ $? -gt 0 ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: buildout return error status"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
some_other_bin_path="$ENCD_HOME/bin/batchupgrade"
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
    sudo -H -u encoded "$ENCD_HOME/bin/create-mapping" "$ENCD_HOME/production.ini" --app-name app
    if [ $? -gt 0 ]; then
        echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: create-mapping return error status"
        # Build has failed
        touch "$encd_failed_flag"
        exit 1
    fi
fi

if [ ! "$ENCD_BUILD_TYPE" == 'app' ]; then
    sudo -H -u encoded "$ENCD_HOME/bin/index-annotations" "$ENCD_HOME/production.ini" --app-name app
    if [ $? -gt 0 ]; then
        echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: index-annotations return error status"
        # Build has failed
        touch "$encd_failed_flag"
        exit 1
    fi
fi
sudo -u root cp /srv/encoded/etc/logging-apache.conf /etc/apache2/conf-available/logging.conf

# Create encoded apache conf
a2conf_src_dir="$ENCD_HOME/cloud-config/configs/apache"
a2conf_dest_file='/etc/apache2/sites-available/encoded.conf'
sudo -u root "$a2conf_src_dir/build-conf.sh" "$a2conf_src_dir" "$a2conf_dest_file"
