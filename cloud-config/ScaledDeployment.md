### Demo Cluster(es-wait) with open postgres port: es-nodes-template.yml and app-pg-template.yml

###### This command builds the Elasticsearch cluster
    $ export CLUSTER_NAME='rc102-scaled'
    $ bin/deploy --cluster-name "$CLUSTER_NAME" --es-wait

        ### Output
        Deploying es-nodes
        $ bin/deploy --cluster-name "$CLUSTER_NAME" --es-wait
        Create instance and wait for running state
        # Deploying Head ES Node(172.31.29.190): encd-dev-open-datamaster
        ###

    The IP address is the --es-ip used to deploy a frontend.
    $ export ES_IP='172.31.30.150' && export CLUSTER_NAME='rc102-scaled'

###### This command builds the front-end machine that connects to the specified elasticsearch cluster with an open postgres port.
    $ bin/deploy --cluster-name "$CLUSTER_NAME" --es-ip "$ES_IP" --pg-open
    
        ### Output
        Deploying app-pg
        $ bin/deploy --cluster-name encd-dev-open --es-ip 172.31.29.190 --pg-open
        Create instance and wait for running state

        Deploying Frontend(172.31.25.255): https://encd-dev.demo.encodedcc.org
        ###


### Demo with postgres and elasticsearch pointing at Demo Cluster: app-template.yml
    $ export PG_IP='172.31.29.226'
    $ bin/deploy -n rc102-scaled-fe01 --cluster-name "$CLUSTER_NAME" --es-ip "$ES_IP" --pg-ip "$PG_IP" --instance-type m5.4xlarge
    $ bin/deploy -n rc102-scaled-fe02 --cluster-name "$CLUSTER_NAME" --es-ip "$ES_IP" --pg-ip "$PG_IP" --instance-type m5.2xlarge
    $ bin/deploy -n rc102-scaled-fe03 --cluster-name "$CLUSTER_NAME" --es-ip "$ES_IP" --pg-ip "$PG_IP" --instance-type m5.xlarge
