#!/bin/bash

# edw_import_cron.sh
#   Script for cron-based (e.g. hourly) import of new ENCODE files at EDW to encoded app
#   TODO: would be good to have lock file to suppress multiple instances (or add to command)

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

hostname=$1
shift
notify=$@

ext=`date +%b%d.%H`
cd /srv/encoded
out=/srv/cron.logs/edw_sync/import.${ext}.log

bin/read-edw-fileinfo -v -I > ${out} 2>&1
success=`grep -c Success ${out}`
fail=`grep -c Fail ${out}`

mail -s "CRON: EDW file sync to ${hostname}. Succeeded: ${success}, Failed: ${fail}" ${notify} < ${out}
