## Architecture of monitoring

Monitoring consists of separate Elasticsearch single node or a cluster and a co-hosted Kibana instance. The separate cluster approach is recommended by the Elastic team due to it's resiliency. In the case that the clusters being monitored are unresponsive, Kibana monitoring will not freeze up. 

The monitoring Elasticsearch cluster will store current and historical stats about production and dev clusters. The data will stay even after the clusters ore retired.


## Installing Monitoring cluster

1. For this step, we take advantage of the existing way of deploying an Elasticsearch cluster. It's a standard cluster configured with Kibana:

		bin/deploy --cluster-name monitoring-for-featurex --cluster-size 1 --jvm-gigs 4 --es-wait --full-build --kibana


## Setting up Elasticsearch cluster to report monitoring statistics
  

1.  Launch cluster with "--monitor" argument from the same encode repo branch. If they have the same branch name, they will link up.

		bin/deploy --cluster-name demo-cluster --es-wait --full-build --monitor --cluster-size 3

2.  Launch the front-end:

        bin/deploy --full-build --es-ip xxx.xx.xx.xxx --name monitored-demo

Kibana interface will be available at [kibana-instance-name].demo.encodedcc.org
