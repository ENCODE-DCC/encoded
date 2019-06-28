#!/bin/bash
# Setup elasticsearch data node config
# root user
# apt deps:
#   java
#   elasticsearch with apt_source and key

CLUSTER_NAME=$1
ES_MASTER=$2
ES_DATA=$3
MIN_MASTER_NODES=$4

# Add options elasticsearch.yml
echo 'network.host: 0.0.0.0' >> /etc/elasticsearch/elasticsearch.yml
echo 'http.port: 9201' >> /etc/elasticsearch/elasticsearch.yml
echo 'transport.tcp.port: 9299' >> /etc/elasticsearch/elasticsearch.yml
echo "node.master: $ES_MASTER" >> /etc/elasticsearch/elasticsearch.yml
echo "node.data: $ES_DATA" >> /etc/elasticsearch/elasticsearch.yml
echo "discovery.zen.minimum_master_nodes: $MIN_MASTER_NODES" >> /etc/elasticsearch/elasticsearch.yml
echo 'discovery.type: ec2' >> /etc/elasticsearch/elasticsearch.yml
echo 'cloud.aws.region: us-west-2' >> /etc/elasticsearch/elasticsearch.yml
echo 'discovery.ec2.groups: elasticsearch-https, ssh-http-https' >> /etc/elasticsearch/elasticsearch.yml
echo 'indices.query.bool.max_clause_count: 8192' >> /etc/elasticsearch/elasticsearch.yml
# Discover Other Nodes
echo "cluster.name: $CLUSTER_NAME" >> /etc/elasticsearch/elasticsearch.yml
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
MEMGIGS=$(awk '/MemTotal/{printf int($2 / 1024**2)}' /proc/meminfo)
if [ "$MEMGIGS" -gt 12 ]
then
   echo "-Xms8g" >> /etc/elasticsearch/jvm.options
   echo "-Xmx8g" >> /etc/elasticsearch/jvm.options
else
   echo "-Xms4g" >> /etc/elasticsearch/jvm.options
   echo "-Xmx4g" >> /etc/elasticsearch/jvm.options
   sysctl "vm.swappiness=1"
   swapon /swapfile
fi
# not sure
update-rc.d elasticsearch defaults
# Discover Other Nodes
sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install discovery-ec2
# restart
service elasticsearch restart
