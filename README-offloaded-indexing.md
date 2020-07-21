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

    # Check apache: /etc/apache2/sites-available/encoded.conf
    App workers should be 8
    indexer should exist
    No vis and region

    # turn off machine so we can check that the head node can turn it on for initial indexing
        * wait for it to stop

    # SSh onto head node and restart apache while watching the error.log
        * wait for the head node to trigger remote indexing
        * make sure remote indexer turns on in AWS

    # Create a dashboard, add the indexer node by hand


# (TBD) Reset indexing and head node states.  
    This will reinitialize the indexing and head node states in es.  

# (TBD) Turn off remote indexing on a live cluster.  Returning it to non remote indexing
    This will update the apache and application ini configs.
