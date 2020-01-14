#!/bin/bash
# Setup encoded app
# encoded user
# apt deps:
echo -e "\n**** ENCDINSTALL $(basename $0) ****"
GIT_REPO="$1"
GIT_REMOTE="$2"
GIT_BRANCH="$3"
ROLE="$4"
ES_IP="$5"
ES_PORT="$6"
REGION_INDEX="$7"
APP_WORKERS="$8"

git_uri="$GIT_REMOTE/$GIT_BRANCH"

encd_home='/srv/encoded'
mkdir "$encd_home"
chown encoded:encoded "$encd_home"
cd "$encd_home"
sudo -u encoded git clone "$GIT_REPO" .
sudo -u encoded git checkout -b "$GIT_BRANCH" "$git_uri"
sudo pip3 install --upgrade pip==19.1.1
sudo pip3 install -U zc.buildout setuptools==43 redis
sudo -u encoded buildout bootstrap
sudo -u encoded LANG=en_US.UTF-8 bin/buildout -c "$ROLE".cfg buildout:es-ip="$ES_IP" buildout:es-port="$ES_PORT"
sudo -u encoded mkdir /srv/encoded/.aws
sudo -u root cp /home/ubuntu/encd-aws-keys/* /srv/encoded/.aws/
sudo -u root chown -R encoded:encoded ~encoded/.aws
until sudo -u postgres psql postgres -c ""; do sleep 10; done
sudo -u encoded sh -c 'cat /dev/urandom | head -c 256 | base64 > session-secret.b64'
sudo -u encoded bin/create-mapping production.ini --app-name app
sudo -u encoded bin/index-annotations production.ini --app-name app
cp /srv/encoded/etc/logging-apache.conf /etc/apache2/conf-available/logging.conf
# Create encoded apache conf
a2conf_src_dir="$encd_home/cloud-config/deploy-run-scripts/conf-apache"
a2conf_dest_file='/etc/apache2/sites-available/encoded.conf'
sudo -u root "$a2conf_src_dir/build-conf.sh" "$REGION_INDEX" "$APP_WORKERS" "$a2conf_src_dir" "$a2conf_dest_file"
