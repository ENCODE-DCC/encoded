#!/bin/bash
cd /Users/casey/_Work/encd-proj/encoded
git push origin split-demo-config:split-demo-config
bin/deploy -b split-demo-config -n ccy-split-t1 >> ~/.ssh/.ssh/config

sleep_time=60
echo "sleeping for $sleep_time waiting for machine to come up"
sleep $sleep_time
ssh ccy-split-t1.ubu "tail -f /var/log/cloud-init-output.log"
if [ $? -eq 0 ]; then
	echo "2nd sleeping for $sleep_time waiting for machine to come up"
	sleep $sleep_time
	ssh ccy-split-t1.ubu "tail -f /var/log/cloud-init-output.log"
	if [ $? -eq 0 ]; then
		echo "not up yet: ssh ccy-split-t1.ubu"
		exit
	fi
fi
echo "sleeping for $sleep_time waiting for reboot"
sleep $sleep_time
ssh ccy-split-t1.ubu
