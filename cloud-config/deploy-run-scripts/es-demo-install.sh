#!/bin/bash
# Setup elastic search config
# root user
# apt deps:
#   java
#   elasticsearch with apt_source and key

# Add options elasticsearch.yml
echo 'http.port: 9201' >> /etc/elasticsearch/elasticsearch.yml
echo 'thread_pool:' >> /etc/elasticsearch/elasticsearch.yml
echo '  search:' >> /etc/elasticsearch/elasticsearch.yml
echo '    size: 100' >> /etc/elasticsearch/elasticsearch.yml
echo '    queue_size: 2000' >> /etc/elasticsearch/elasticsearch.yml
echo '  index:' >> /etc/elasticsearch/elasticsearch.yml
echo '    queue_size: 400' >> /etc/elasticsearch/elasticsearch.yml
echo 'indices.query.bool.max_clause_count: 8192' >> /etc/elasticsearch/elasticsearch.yml
# Add options jvm.options
echo '-XX:+UseConcMarkSweepGC' >> /etc/elasticsearch/jvm.options
echo '-XX:CMSInitiatingOccupancyFraction=75' >> /etc/elasticsearch/jvm.options
echo '-XX:+UseCMSInitiatingOccupancyOnly' >> /etc/elasticsearch/jvm.options
echo '-XX:+DisableExplicitGC' >> /etc/elasticsearch/jvm.options
echo '-XX:+AlwaysPreTouch' >> /etc/elasticsearch/jvm.options
echo '-server' >> /etc/elasticsearch/jvm.options
echo '-Xss1m' >> /etc/elasticsearch/jvm.options
echo '-Djava.awt.headless=true' >> /etc/elasticsearch/jvm.options
echo '-Dfile.encoding=UTF-8' >> /etc/elasticsearch/jvm.options
echo '-Djna.nosys=true' >> /etc/elasticsearch/jvm.options
echo '-Djdk.io.permissionsUseCanonicalPath=true' >> /etc/elasticsearch/jvm.options
echo '-Dio.netty.noUnsafe=true' >> /etc/elasticsearch/jvm.options
echo '-Dio.netty.noKeySetOptimization=true' >> /etc/elasticsearch/jvm.options
echo '-Dio.netty.recycler.maxCapacityPerThread=0' >> /etc/elasticsearch/jvm.options
echo '-Dlog4j.shutdownHookEnabled=false' >> /etc/elasticsearch/jvm.options
echo '-Dlog4j2.disable.jmx=true' >> /etc/elasticsearch/jvm.options
echo '-Dlog4j.skipJansi=true' >> /etc/elasticsearch/jvm.options
echo '-XX:+HeapDumpOnOutOfMemoryError' >> /etc/elasticsearch/jvm.options
# Set available java memory
MEMGIGS=$(awk '/MemTotal/{printf "%.0f", $2 / 1024**2}' /proc/meminfo)
if [ "$MEMGIGS" -gt 32 ]
then
   echo "-Xms8g" >> /etc/elasticsearch/jvm.options
   echo "-Xmx8g" >> /etc/elasticsearch/jvm.options
elif [ "$MEMGIGS" -gt 12 ]
then
   echo "-Xms4g" >> /etc/elasticsearch/jvm.options
   echo "-Xmx4g" >> /etc/elasticsearch/jvm.options
else
   echo "-Xms2g" >> /etc/elasticsearch/jvm.options
   echo "-Xmx2g" >> /etc/elasticsearch/jvm.options
   sysctl "vm.swappiness=1"
   swapon /swapfile
fi
# not sure
update-rc.d elasticsearch defaults
# restart
service elasticsearch restart
