Organization deployment configuration and build files
=====================================================
    When bin/deploy is run user_data is sent to AWS.  The user_data defines the type of deployment,
    i.e. Demo, es cluster, frontend, etc.  The user_data is compiled in two stages.  The first
    stage creates an Assembled Template.  By default the template is in memory but a bin/deploy
    argument exists that allows the assembled template to be saved and used later.  The second stage
    adds Run Variables to the Assembled Template.  Then it can be sent as user_data to AWS to create
    an instance.

# Summary of cloud-config directory structure

#### Templates are assembled with ./template-parts
    # Standard Templates
    Demo/QA Demo                : app-es-pg-template.yml
    Cluster Frontend            : app-pg-template.yml
    Cluster Elasticsearch       : es-nodes-template.yml

    # Non Standard Templates
    Instance with remote pg     : app-es-template.yml
    Instance with remote pg/es  : app-template.yml

    Open one of the templates above to compare with ./template-parts.  Each variable '%(varname)s'
    in the template has a matching file in ./template-parts.  Next is a way to view and save
    assembled templates.

    We can save Assembled Templates with the --save-configure bin/deploy argument.  It will
    automaticallly determine which template to used based on input arguments.

    $ bin/deploy --save-config-name 20200430

    ### Output
    Created assembeled template
           ./cloud-config/assembled-templates/20200430-app-es-pg.yml
    Deploy with
           $ bin/deploy --use-prebuilt-config 20200430-app-es-pg
    Diff with on the fly assembly.  Does not deploy
           $ bin/deploy --use-prebuilt-config 20200430-app-es-pg --diff-configs
    ###


#### Directories:
    template-parts              : Pieces of the templates
    run-scripts                 : Install scripts runcmd_* template parts
    configs                     : Configuration files used in run-scripts, like apache, java, es
    assembled-templates         : Saved.  These still contains Run Varialbes

#### Helper Script
    create-ami.py               : Create amis from deployed --ami-build in AWS

#### Run_Variables
    * Run variables are in /etc/environment file on the instance.  
    * They are used in the run-scripts to configure the system and application builds
    * /etc/environment is loaded into login/ssh sessions so you can echo them on the instance.
    * The file will contain dupicate entries when deploying from an AMI.  Last ones are used.

    View them locally with --dry-run along with other info.  Does not deploy
    $ bin/deploy --dry-run

    Add options like --test, --release-candidate, or --candidate to see the differences in run vars.
    The ROLE should change along with other variables like ENCD_INDEX_PRIMARY, ENCD_INDEX_VIS,
    ENCD_INDEX_REGION.  The env vars are prefixed with ENCD_ as to not conflict with other env vars.

# Live Deployments
    Below we'll deploy demos and clusters using the --full-build argument to avoid needing amis.  
    Building from scratch is easier for cloud config development.

### QA/Development demo: app-es-pg-template.yml
    $ bin/deploy --full-build

        ### Output
        Deploying app-es-pg
        $ bin/deploy --full-build
        create instance and wait for running state
        ####

### Demo Cluster(es-wait): es-nodes-template.yml and app-pg-template

###### This command builds the Elasticsearch cluster
    $ export CLUSTER_NAME='encd-dev'
    $ bin/deploy --full-build --cluster-name "$CLUSTER_NAME" --es-wait

        ### Output
        Deploying es-nodes
        $ bin/deploy --full-build --cluster-name "$CLUSTER_NAME" --es-wait
        Create instance and wait for running state
        # Deploying Head ES Node(172.31.26.236): encd-dev-datamaster
        ###

    The IP address is the --es-ip used to deploy a frontend.
    $ export ES_IP='172.31.26.236'


###### This command builds the front-end machine that connects to the specified elasticsearch cluster
    $ bin/deploy --full-build --cluster-name "$CLUSTER_NAME" --es-ip "$ES_IP"

        ### Output
        Deploying app-pg
        $ bin/deploy --full-build --cluster-name encd-dev --es-ip 172.31.26.236
        Create instance and wait for running state

        Deploying Frontend(172.31.23.80): https://encd-dev.demo.encodedcc.org
        ###

### QA/Development demo with postgres pointing at Demo Cluster: app-pg-template.yml
    $ bin/deploy --full-build -n app-pg-pointing-at-es --es-ip "$ES_IP" --no-indexing


### Demo Cluster(es-wait) with open postgres port: es-nodes-template.yml and app-pg-template.yml

###### This command builds the Elasticsearch cluster
    $ export CLUSTER_NAME='encd-dev-open'
    $ bin/deploy --full-build --cluster-name "$CLUSTER_NAME" --es-wait

        ### Output
        Deploying es-nodes
        $ bin/deploy --full-build --cluster-name "$CLUSTER_NAME" --es-wait
        Create instance and wait for running state
        # Deploying Head ES Node(172.31.29.190): encd-dev-open-datamaster
        ###

    The IP address is the --es-ip used to deploy a frontend.
    $ export ES_IP='172.31.29.190'

###### This command builds the front-end machine that connects to the specified elasticsearch cluster with an open postgres port.
    $ bin/deploy --full-build --cluster-name "$CLUSTER_NAME" --es-ip "$ES_IP" --pg-open

        ### Output
        Deploying app-pg
        $ bin/deploy --full-build --cluster-name encd-dev-open --es-ip 172.31.29.190 --pg-open
        Create instance and wait for running state

        Deploying Frontend(172.31.25.255): https://encd-dev.demo.encodedcc.org
        ###


### Demo with postgres and elasticsearch pointing at Demo Cluster: app-template.yml
    $ export PG_IP='172.31.25.255'
    $ bin/deploy --full-build -n app-pointing-at-pg-es --cluster-name "$CLUSTER_NAME" --es-ip "$ES_IP" --pg-ip "$PG_IP"


### (TBD) Demo with elasticsearch pointing at rds version of postgres: app-es-template.yml



### Cluster with remote indexing node, this a little manual since deploy vars are getting messy
    $ export GIT_REL='v103rc2' && export ENCD_REL='v103rc2' && echo "$GIT_REL $ENCD_REL"

    # Normal elasticsearch cluster
    $ bin/deploy -b "$GIT_REL" --cluster-name "$ENCD_REL" --es-wait --dry-run
        RC:   --release-candidate
        Test: --test
        Prod: --profile-name production --candidate

    # Head frontend node: 12 app workers, 8 index workers
    $ export ES_IP=172.31.25.24
    $ bin/deploy -b $GIT_REL --es-ip $ES_IP --cluster-name "$ENCD_REL" --remote-indexing --primary-indexing --index-procs 8 --app-workers 12 --pg-open --do-batchupgrade no --dry-run
        RC:   --release-candidate
        Test: --test
        Prod: --profile-name production --candidate

    # Check environment vars
    $ cat /etc/environment
        * ENCD_APP_WORKERS=12
        * ENCD_INDEX_PROCS=8
        * ENCD_REMOTE_INDEXING=true

    # ssh on and stop apache after the instance restart
    $ sudo service apache2 stop

    # Check encoded base.ini
    [composite:indexer]
    set queue_worker_processes = 8
    set remote_indexing = true
    set remote_indexing_threshold = 10001

    # Check apache
    App workers should be 12
    indexer, vis, and region should exist

    # Indexer node: 8 app workers, 16 index workers
    $ export PG_IP=172.31.30.133
    $ bin/deploy -b $GIT_REL --es-ip $ES_IP --pg-ip $PG_IP -n "$ENCD_REL-indexer" --cluster-name "$ENCD_REL" --no-indexing --primary-indexing --app-workers 8 --do-batchupgrade no --dry-run
        RC:   --release-candidate
        Test: --test
        Prod: --profile-name production --candidate

    # Check environment vars
    $ cat /etc/environment
        * ENCD_APP_WORKERS=8
        * ENCD_INDEX_PROCS=16
        * ENCD_INDEX_PRIMARY=true
        * ENCD_INDEX_VIS=false
        * ENCD_INDEX_REGION=false
        * ENCD_REMOTE_INDEXING=false

    # Check encoded base.ini
    [app:app]
    sqlalchemy.url = postgresql://172.31.30.133/encoded
    [composite:indexer]
    set queue_worker_processes = 16
    set remote_indexing = false
    set remote_indexing_threshold = 10001

    # Check apache
    App workers should be 8
    indexer should exist
    No vis and region

    # turn off machine so we can check that the head node can turn it on for initial indexing
        * wait for it to stop

    # SSh onto head node and restart apache while watching the error.log
        * wait for the head node to trigger remote indexing
        * make sure remote indexer turns on in AWS

    # Create a dashboard, add the indexer node by hand
