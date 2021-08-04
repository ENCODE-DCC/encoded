#!/bin/bash
# Setup redis config
echo -e "\n$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
# Backup default redis config
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.default
# Switch redis port
sudo sed -i -e "s/port 6379/port $ENCD_REDIS_PORT/" /etc/redis/redis.conf
# Allow remote connections
sudo sed -i -e 's/bind 127\.0\.0\.1/bind 0\.0\.0\.0/' /etc/redis/redis.conf
# Set maxmemory
echo "maxmemory 5GB" | sudo tee -a /etc/redis/redis.conf
# Set eviction policy
echo "maxmemory-policy allkeys-lru" | sudo tee -a /etc/redis/redis.conf
# restart
sudo service redis-server restart
