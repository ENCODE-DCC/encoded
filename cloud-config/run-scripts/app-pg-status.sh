#!/bin/bash
# Wait for psql command to return
echo -e "\n$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Wait for postgres to restart"
psql_cnt=0
until sudo -u postgres psql postgres -c ""; do
    watch_dog=$((watch_dog + 1))
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) waiting for $sleep_secs"
    sleep 10;
    if [ $watch_dog -gt 10 ]; then
        echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Restart Failed"
        # Build has failed
        touch "$encd_failed_flag"
        exit 1
    fi
done
