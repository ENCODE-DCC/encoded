#!/bin/bash
# Setup encoded app
# encoded user
# apt deps:
echo -e "\n**** ENCDINSTALL $(basename $0) ****"

ROLE="$1"
ES_IP="$2"
ES_PORT="$3"
REGION_INDEX="$4"
APP_WORKERS="$5"

encd_pybin='/srv/encoded/.pyvenv/bin'
encd_home='/srv/encoded'
cd "$encd_home"
sudo -u encoded "$encd_pybin/buildout" bootstrap
sudo -u encoded LANG=en_US.UTF-8 bin/buildout -c "$ROLE".cfg buildout:es-ip="$ES_IP" buildout:es-port="$ES_PORT"

# Add aws keys to encoded user
sudo -u encoded mkdir /srv/encoded/.aws
sudo -u root cp /home/ubuntu/encd-aws-keys/* /srv/encoded/.aws/
sudo -u root chown -R encoded:encoded ~encoded/.aws

# Add ssh keys to encoded user
sudo -u encoded mkdir /srv/encoded/.ssh
sudo -u root cp /home/ubuntu/.ssh/authorized_keys2 /srv/encoded/.ssh/authorized_keys2
sudo -u root chown -R encoded:encoded /srv/encoded/.ssh/authorized_keys2

# Wait for psql
until sudo -u postgres psql postgres -c ""; do sleep 10; done
sudo -u encoded sh -c 'cat /dev/urandom | head -c 256 | base64 > session-secret.b64'
sudo -u encoded bin/create-mapping production.ini --app-name app
sudo -u encoded bin/index-annotations production.ini --app-name app
cp /srv/encoded/etc/logging-apache.conf /etc/apache2/conf-available/logging.conf
# Create encoded apache conf
a2conf_src_dir="$encd_home/cloud-config/deploy-run-scripts/conf-apache"
a2conf_dest_file='/etc/apache2/sites-available/encoded.conf'
sudo -u root "$a2conf_src_dir/build-conf.sh" "$REGION_INDEX" "$APP_WORKERS" "$a2conf_src_dir" "$a2conf_dest_file"
