#!/bin/bash
# Check es status
echo -e "\n$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
# Wait for es to come up on demos and frontends
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Waiting for es to come up"
# wait for status to be yellow or green
watch_dog=0
while true; do
    watch_dog=$((watch_dog + 1))
    es_status="$(curl -fsSL $ELASTICSEARCH_URL/_cat/health?h=status)"
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) status: '$es_status'"
    if [ "$es_status" == 'yellow' ] || [ "$es_status" == 'green' ]; then
        echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) status passed"
        exit 0
    else
        sleep_secs=10
        echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) waiting for $sleep_secs"
        sleep $sleep_secs
    fi
    if [ $watch_dog -gt 10 ]; then
        echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: ES status watchdog"
        # Build has failed
        touch "$encd_failed_flag"
        exit 1
    fi
done
