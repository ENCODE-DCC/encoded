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
# Add config for LRU cache
echo "maxmemory 24gb" | sudo tee -a /etc/redis/redis.conf > /dev/null
echo "maxmemory-policy allkeys-lru" | sudo tee -a /etc/redis/redis.conf > /dev/null
# Turn off persistence
sudo sed -i -e 's/^save/#\ save/' /etc/redis/redis.conf
# Turn off daemonize, for some reason it is set to yes in default conf which conflicts with systemd
sudo sed -i -e 's/^daemonize/#\ daemonize/' /etc/redis/redis.conf
# Make sure supervised is set correctly, was `no` in original conf
sudo sed -i -e 's/^supervised\ no/supervised\ systemd/' /etc/redis/redis.conf
echo 'save ""' | sudo tee -a /etc/redis/redis.conf > /dev/null

# Disable THP, see https://docs.mongodb.com/manual/tutorial/transparent-huge-pages/
echo "never" > /sys/kernel/mm/transparent_hugepage/enabled
sudo cp "$ENCD_CC_DIR/configs/redis/disable-transparent-huge-pages.service" /etc/systemd/system/disable-transparent-huge-pages.service
sudo systemctl daemon-reload
sudo systemctl start disable-transparent-huge-pages
sudo systemctl enable disable-transparent-huge-pages

# restart
sudo service redis-server restart
