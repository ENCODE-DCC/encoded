#!/bin/sh

# Encode Nginx proxy server setup.
# Assumes ssl.tgz present containing SSL certs / keys.

# Use the nginx/stable ppa as we want the current nginx.
apt-get install software-properties-common
add-apt-repository -y ppa:nginx/stable
apt-get update
apt-get install -y curl dnsmasq nginx-full ntp unattended-upgrades update-notifier-common

# Enable automatic security updates. This does not cover nginx as it is from a ppa.
cat <<'EOF' > /etc/apt/apt.conf.d/20auto-upgrades
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

# Quoting 'EOF' prevents $variable substitution
cat <<'EOF' > /etc/apt/apt.conf.d/50unattended-upgrades
Unattended-Upgrade::Allowed-Origins {
    "${distro_id} ${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "true";
EOF

mkdir -p /etc/nginx/ssl
tar -zxf ssl.tgz --directory /etc/nginx/ssl
# Generate a new (takes a few minutes.)
openssl dhparam 2048 -out /etc/nginx/ssl/dhparam.pem
chmod 600 /etc/nginx/ssl/dhparam.pem

curl -o /etc/nginx/nginx.conf https://raw.githubusercontent.com/ENCODE-DCC/encoded/master/encode-proxy-nginx.conf

service nginx restart
