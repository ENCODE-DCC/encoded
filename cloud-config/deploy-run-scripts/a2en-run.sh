#!/bin/bash
# Setup stuff after other installs
# root user
# apt deps:
echo -e "\n**** ENCDINSTALL $(basename $0) ****"
a2enmod headers
a2enmod proxy_http
a2enmod rewrite
a2enmod ssl
a2enmod log_forensic
a2ensite encoded.conf
a2dissite 000-default
a2enconf logging
a2disconf charset
a2disconf security
a2disconf localized-error-pages
a2disconf other-vhosts-access-log
a2disconf serve-cgi-bin
