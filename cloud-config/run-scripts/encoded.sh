#!/bin/bash
# Setup encoded app
echo -e "$(basename $0) Running"

# Install App
cd "$encd_home"

# Run bootstrap
sudo -H -u encoded "$encd_home/.pyvenv/bin/buildout" bootstrap
bin_build_path="$encd_home/bin/buildout"

# Run bin/buildout
bin_build_cmd="$encd_home/bin/buildout -c $encd_role.cfg"
echo -e "$(basename $0) CMD: $bin_build_cmd"
sudo -H -u encoded LANG=en_US.UTF-8 $bin_build_cmd

# Downlaod encoded demo aws keys
encd_keys_dir=/home/ubuntu/encd-aws-keys
mkdir "$encd_keys_dir"
aws s3 cp --region=us-west-2 --recursive s3://encoded-conf-prod/encd-aws-keys "$encd_keys_dir"
# Add aws keys to encoded user
sudo -u encoded mkdir /srv/encoded/.aws
sudo -u root cp /home/ubuntu/encd-aws-keys/* /srv/encoded/.aws/
sudo -u root chown -R encoded:encoded ~encoded/.aws

# Finished running post pg scripts
sudo -H -u encoded sh -c 'cat /dev/urandom | head -c 256 | base64 > session-secret.b64'
sudo -H -u encoded "$encd_home/bin/create-mapping" "$encd_home/production.ini" --app-name app
sudo -H -u encoded "$encd_home/bin/index-annotations" "$encd_home/production.ini" --app-name app
sudo -u root cp /srv/encoded/etc/logging-apache.conf /etc/apache2/conf-available/logging.conf

# Create encoded apache conf
a2conf_src_dir="$encd_home/cloud-config/configs/apache"
a2conf_dest_file='/etc/apache2/sites-available/encoded.conf'
sudo -u root "$a2conf_src_dir/build-conf.sh" "$a2conf_src_dir" "$a2conf_dest_file"

sudo -u root $encd_home/cloud-config/run-scripts/a2en.sh
if [ "$encd_batchupgrade" == "true" ]; then
    $encd_home/cloud-config/run-scripts/batchupgrade.sh production.ini "$batchupgrade_vars"
fi

sudo apt --fix-broken install
sudo DEBIAN_FRONTEND=noninteractive apt install -y postfix
sudo sed -i -e 's/inet_interfaces = all/inet_interfaces = loopback-only/g' /etc/postfix/main.cf
PUBLIC_DNS_NAME="$(curl http://169.254.169.254/latest/meta-data/public-hostname)"
sudo sed -i "/myhostname/c\myhostname = $PUBLIC_DNS_NAME" /etc/postfix/main.cf
sudo echo "127.0.0.0 $PUBLIC_DNS_NAME" | sudo tee --append /etc/hosts
sudo mv /etc/mailname /etc/mailname.OLD
sudo echo "$PUBLIC_DNS_NAME" | sudo tee --append /etc/mailname
sudo service postfix restart
