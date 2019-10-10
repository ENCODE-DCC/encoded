## Architecture of monitoring

Monitoring consists of separate Elasticsearch single node or a cluster and a co-hosted Kibana instance. The separate cluster approach is recommended by the Elastic team due to it's resiliency. In the case that the clusters being monitored are unresponsive, Kibana monitoring will not freeze up. 

The monitoring Elasticsearch cluster will store current and historical stats about production and dev clusters. The data will stay even after the clusters ore retired.


## Installing Monitoring cluster

1. For this step, we take advantage of the existing way of deploying an Elasticsearch cluster

		bin/deploy --cluster-name monitoring --cluster-size 3 --instance-type m5.large --jvm-gigs 4 --es-elect

2. Install x-pack on each node:

		sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install x-pack

3. Disable x-pack default security (/etc/elasticsearch/elasticsearch.yml)

		xpack.security.enabled: false

4. Restart each node

		sudo service elasticsearch restart

Monitoring cluster could also be a single node. That's how it will be in production. Each production release will have a monitoring node that's deployed with Kibana.


## Setting up Elasticsearch cluster to report monitoring statistics
  

1.  Install xpack

			sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install x-pack

2.  On each node of the cluster, we add a setting to disable x-pack security and then tell the node where to send the statistics (/etc/elasticsearch/elasticsearch.yml):

		xpack.security.enabled: false
		xpack.monitoring.exporters:
			id1:
				type: http
				host: ["http://monitoring-data0.instance.encodedcc.org:9201", "http://monitoring-data1.instance.encodedcc.org:9201", "http://monitoring-data2.instance.encodedcc.org:9201"]

  

3.  Disable shard allocation temporarily:

		

		curl -X PUT "localhost:9201/_cluster/settings?pretty" -H 'Content-Type: application/json' -d'
		{
			"transient": {
				"cluster.routing.allocation.enable": "none"
			}
		}'

4.  Restart the node

		sudo service elasticsearch restart

5.  Re-enable allocation

		

		curl -X PUT "localhost:9201/_cluster/settings?pretty" -H 'Content-Type: application/json' -d'
		{
			"transient": {
				"cluster.routing.allocation.enable": "all"
			}
		}'

6.  check status of the node

		curl -X GET "localhost:9201/_cat/health?pretty"
		curl -X GET "localhost:9201/_cat/recovery?pretty"

IMPORTANT: Steps 3-6 must be done sequentially on a node. Only after the successful recovery of the node shards you should move on doing the steps 3-6 on the next node.

At this point, the cluster statistics should be showing up in Kibana.

## Installing Kibana

Kibana is lightweight enough to run on one of the nodes of the monitoring cluster. So, the steps assume that the host is shared between Kibana and one of the Elasticsearch monitoring cluster node.

1.  Install Kibana

		sudo apt-get install kibana
		

2. Install x-pack as the kibana user

		sudo -u kibana /usr/share/kibana/bin/kibana-plugin install x-pack

3.  Update Kibana settings

		xpack.security.enabled: false
		elasticsearch.url: "http://localhost:9201"
		server.host: 0.0.0.0

4. Restart Kibana

		sudo service kibana restart

Kibana interface will be available at the host:5601. The user IP address range must be added to the `kibana` security group on AWS for the interface to be accessible.


		

