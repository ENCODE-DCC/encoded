#!/bin/bash
# Wait for psql command to return
echo -e "\n$(basename $0) Running"
psql_cnt=0
until sudo -u postgres psql postgres -c ""; do
    watch_dog=$((watch_dog + 1))
    echo -e "$(basename $0) waiting for $sleep_secs"
    sleep 10;
    if [ $watch_dog -gt 10 ]; then
        echo -e "$(basename $0) Restart Failed"
        # Build has failed
        exit 1
    fi
done
