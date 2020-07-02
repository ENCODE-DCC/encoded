# Main Deployments and tags

## Demo (demo)
    $ export GIT_REL='dev' && export ENCD_REL='dev-demo' && echo "$GIT_REL $ENCD_REL"
    $ bin/deploy --dry-run -b $GIT_REL -n $ENCD_REL

    ## Important Demo node tags ## 
    section                     :'app-dev'
    Name                        :'dev-demo'
    branch                      :'dev'
    ec_cluster_name             :'single'
    auto_shutdown               :'true'
    auto_resize                 :'c5.4xlarge'
    Role                        :'encd-dev'


## Demo cluster (democ)
    $ export GIT_REL='dev' && export ENCD_REL='dev-democ' && echo "$GIT_REL $ENCD_REL"
    $ bin/deploy --dry-run -b $GIT_REL --cluster-name "$ENCD_REL" --es-wait

    ## Important Demo elasticsearch node tags ##
    section                     :'app-dev-cluster'
    Name                        :'dev-democ'
    branch                      :'dev'
    elasticsearch               :'yes'
    elasticsearch_head          :'no'
    ec_cluster_name             :'dev-democ-cluster'
    auto_shutdown               :'true'
    auto_resize                 :'na'
    Role                        :'encd-dev-cluster-data'

    $ export ES_IP='1.2.3.4' && echo "$GIT_REL $ENCD_REL $ES_IP"
    $ bin/deploy --dry-run -b "$GIT_REL" --cluster-name "$ENCD_REL" --es-ip "$ES_IP"
    
    ## Important Demo head frontend node tags ##
    section                     :'app-dev-cluster'
    Name                        :'dev-democ'
    branch                      :'dev'
    elasticsearch               :'no'
    elasticsearch_head          :'no'
    ec_cluster_name             :'dev-democ-cluster'
    auto_shutdown               :'true'
    auto_resize                 :'c5.4xlarge'
    Role                        :'encd-dev-cluster'


## Release Canidate (rc)
    $ export GIT_REL='v100rc1' && export ENCD_REL='v100rc1' && echo "$GIT_REL $ENCD_REL"
    $ bin/deploy --dry-run -b "$GIT_REL" --cluster-name "$ENCD_REL" --es-wait --release-candidate

    ## Important RC elasticsearch node tags ##
    section                     :'app-rc'
    Name                        :'v100rc1'              
    branch                      :'v100rc1'
    elasticsearch               :'yes'
    elasticsearch_head          :'no'                   # 'yes' if -datahead
    ec_cluster_name             :'v100rc1-cluster'
    auto_shutdown               :'false'
    auto_resize                 :'na'
    Role                        :'encd-new-rc-data'     # 'encd-new-rc-datahead'

    $ export ES_IP='1.2.3.4' && echo "$GIT_REL $ENCD_REL $ES_IP"
    $ bin/deploy --dry-run -b "$GIT_REL" --cluster-name "$ENCD_REL" --es-ip "$ES_IP" --release-candidate

    ## Important RC head frontend node tags ##
    section                     :'app-rc'
    Name                        :'v100rc1'
    branch                      :'v100rc1'
    elasticsearch               :'no'
    elasticsearch_head          :'no'
    ec_cluster_name             :'v100rc1-cluster'
    auto_shutdown               :'false'
    auto_resize                 :'na'
    Role                        :'encd-new-rc'


## Test (test)
    $ export GIT_REL='v100.0' && export ENCD_REL='v100x0-test' && echo "$GIT_REL $ENCD_REL"
    $ bin/deploy --dry-run -b "$GIT_REL" --cluster-name "$ENCD_REL" --es-wait --test
    
    ## Important Test elasticsearch node tags ##
    section                     :'app-test'
    Name                        :'v100x0-test'
    branch                      :'v100.0'
    elasticsearch               :'yes'
    elasticsearch_head          :'no'
    ec_cluster_name             :'v100x0-test-cluster'
    auto_shutdown               :'false'
    auto_resize                 :'na'
    Role                        :'encd-new-test-data'


    $ export ES_IP='172.31.28.138' && echo "$GIT_REL $ENCD_REL $ES_IP"
    $ bin/deploy -b "$GIT_REL" --cluster-name "$ENCD_REL" --es-ip "$ES_IP"
    
    ## Important Test head frontend node tags ##



## Production (prod)
    $ export GIT_REL='v100.0' && export ENCD_REL='v100x0' && echo "$GIT_REL $ENCD_REL"
    $ bin/deploy --dry-run -b "$GIT_REL" --cluster-name "$ENCD_REL" --es-wait --profile-name production --candidate
   
    ## Important Prod elasticsearch node tags ##
    section                     :'app-prod'
    account                     :'encode-prod'
    Name                        :'v100x0'
    branch                      :'v100.0'
    elasticsearch               :'yes'
    elasticsearch_head          :'no'
    ec_cluster_name             :'v100x0-cluster'
    auto_shutdown               :'false'
    auto_resize                 :'na'
    Role                        :'encd-new-prod-data'

    $ export ES_IP='1.2.3.4' && echo "$GIT_REL $ENCD_REL $ES_IP"
    $ bin/deploy --dry-run -b "$GIT_REL" --cluster-name "$ENCD_REL" --profile-name production --candidate --es-ip "$ES_IP"

    ## Important Prod head frontend node tags ##
    section                     :'app-prod'
    account                     :'encode-prod'
    Name                        :'v100x0'
    branch                      :'v100.0'
    elasticsearch               :'no'
    elasticsearch_head          :'no'
    ec_cluster_name             :'v100x0-cluster'
    auto_shutdown               :'false'
    auto_resize                 :'na'
    elastic_ip_swtich_datatime  :'pending'
    Role                        :'encd-new-prod'
