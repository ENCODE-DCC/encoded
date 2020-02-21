#!/bin/bash
# Setup stuff after other installs
echo -e "\n$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
a2dismod mpm_event
a2enmod headers
a2enmod proxy_http
a2enmod rewrite
a2enmod ssl
a2enmod log_forensic
a2enmod mpm_worker
a2ensite encoded.conf
a2dissite 000-default
a2enconf logging
a2disconf charset
a2disconf security
a2disconf localized-error-pages
a2disconf other-vhosts-access-log
a2disconf serve-cgi-bin
