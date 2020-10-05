#!/bin/bash
source $ENCD_SCRIPTS_DIR/ami-helpers.sh

if [ "$ENCD_KIBANA" == 'true' ]; then
    # Location of kibana configuration file and intended destination
    opts_src="$ENCD_CC_DIR/configs/kibana"
    opts_dest='/etc/kibana'

    copy_with_permission "$opts_src/es-kibana.yml" "$opts_dest/kibana.yml"
    copy_with_permission "$ENCD_CC_DIR/configs/nginx/nginx-kibana.conf" "/etc/nginx/sites-enabled/default"

    # Download password file for kibana basic auth
    sudo pip3 install --upgrade awscli
    sudo aws s3 cp --region=us-west-2 s3://encode-kibana/kibana.htpasswd /etc/nginx/conf.d/kibana.htpasswd

    # Easier access to conf files
    sudo usermod -a -G kibana ubuntu
    sudo usermod -a -G nginx ubuntu
    sudo chown -R kibana:kibana /etc/kibana //usr/share/kibana

    # Add kibana service and start kibana
    sudo systemctl enable kibana.service
    sudo systemctl start kibana.service
    sudo systemctl enable nginx.service
    sudo systemctl start nginx.service
fi
