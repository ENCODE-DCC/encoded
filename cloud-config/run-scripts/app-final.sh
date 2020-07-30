#!/bin/bash
# Setup stuff after other installs
echo -e "\n$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
if [ "$ENCD_BUILD_TYPE" == 'es-nodes' ]; then
    # For es builds we do not have an app-wrapper.sh
    # This script is called directly in the es runcmd
    # after ami-elasticsearch.sh, which sets encd_is_installed_flag
    if [ ! -f "$encd_is_installed_flag" ]; then
        echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping ES AMI build"
        exit 0
    fi
fi
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
sudo apt --fix-broken install
sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix
sudo sed -i -e 's/inet_interfaces = all/inet_interfaces = loopback-only/g' /etc/postfix/main.cf
PUBLIC_DNS_NAME="$(curl http://169.254.169.254/latest/meta-data/public-hostname)"
sudo sed -i "/myhostname/c\myhostname = $PUBLIC_DNS_NAME" /etc/postfix/main.cf
sudo echo "127.0.0.0 $PUBLIC_DNS_NAME" | sudo tee --append /etc/hosts
sudo mv /etc/mailname /etc/mailname.OLD
sudo echo "$PUBLIC_DNS_NAME" | sudo tee --append /etc/mailname
sudo service postfix restart

# Add team ssh public keys from s3
auth_keys_file='/home/ubuntu/.ssh/authorized_keys'
auth_keys_file2='/home/ubuntu/.ssh/authorized_keys2'
mv "$auth_keys_file" "$auth_keys_file2"
aws s3 cp --region=$ENCD_AWS_REGION $ENCD_S3_AUTH_KEYS "$auth_keys_file"
if [ ! -f "$auth_keys_file" ] || [ ! -f "$auth_keys_file2" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: ssh auth keys"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
