#!/bin/bash
# Check es status
echo -e "\n$(basename $0) Running"
watch_dog=0
while true; do
    watch_dog=$((watch_dog + 1))
    es_status="$(curl -fsSL $encd_es_ip:$encd_es_port/_cat/health?h=status)"
    echo -e "$(basename $0) status: '$es_status'"
    if [ "$es_status" == 'yellow' ] || [ "$es_status" == 'green' ]; then
        echo -e "$(basename $0) status passed"
        exit 0
    else
        sleep_secs=10
        echo -e "$(basename $0) waiting for $sleep_secs"
        sleep $sleep_secs
    fi
    if [ $watch_dog -gt 10 ]; then
        echo -e "$(basename $0) ENCD FAILED: ES status watchdog"
        # Build has failed
        exit 1
    fi
done
