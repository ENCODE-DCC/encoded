#!/bin/bash
# Setup stuff after other installs
# ? user
# apt deps:

a2enmod headers
a2enmod proxy_http
a2enmod rewrite
a2enmod ssl
a2ensite encoded.conf
a2dissite 000-default
a2enconf logging
a2disconf charset
a2disconf security
a2disconf localized-error-pages
a2disconf other-vhosts-access-log
a2disconf serve-cgi-bin
if test "%(ROLE)s" = "demo"
then
  sudo -i -u encoded bin/batchupgrade production.ini --app-name app
fi
sudo sed -i -e 's/inet_interfaces = all/inet_interfaces = loopback-only/g' /etc/postfix/main.cf
PUBLIC_DNS_NAME="$(curl http://169.254.169.254/latest/meta-data/public-hostname)"
sudo sed -i "/myhostname/c\myhostname = $PUBLIC_DNS_NAME" /etc/postfix/main.cf
sudo echo "127.0.0.0 $PUBLIC_DNS_NAME" | sudo tee --append /etc/hosts
sudo mv /etc/mailname /etc/mailname.OLD
sudo echo "$PUBLIC_DNS_NAME" | sudo tee --append /etc/mailname
sudo service postfix restart
