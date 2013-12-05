#!/bin/bash

# edw_compare_cron.sh
#   Script for cron-based (e.g. nightly) inventory of ENCODE files at EDW and encoded app

hostname=$1
shift
notify=$@

ext=`date +%b%d.%H`

cd /srv/encoded
out=/srv/cron.logs/edw_sync/compare.${ext}

bin/read-edw-fileinfo -C -q >${out}.tsv 2> ${out}.log
diff=`grep -c APP_DIFF ${out}.tsv`
edw=`grep -c EDW_ONLY ${out}.tsv`
app=`grep -c APP_ONLY ${out}.tsv`

(cat ${out}.log; echo "Comparison file: ${out}.tsv") | mail -s "CRON: EDW file compare to ${hostname}. Diffs: ${diff}, EDW only: ${edw}, App only: ${app}" ${notify} $notify
