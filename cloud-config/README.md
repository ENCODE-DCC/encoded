Organization deployment configuration and build files
=====================================================


## Example commands

# Deploy with ubuntu 18 base ami
    ```
    Demo
    $ bin/deploy -n test-demo --full-build
        "cycle_started": "2020-04-21T22:19:47.923214",
        "indexed": 1392520,
        "cycle_took": "3:31:02.360139"
    
    Demo Cluster
    $ bin/deploy --cluster-name test-wait --full-build --es-wait
    used by Frontend with postgres
    $ bin/deploy --cluster-name test-wait --full-build --es-ip a.b.c.d 
    ```

# Build and save a cloud config yml
    ```
    Demo
    $ bin/deploy --save-config-name 20200421 
   
    ES Node - wait
    $ bin/deploy --save-config-name 20200421 --es-wait --cluster-name some-name

    ES Node - elect
    $ bin/deploy --save-config-name 20200421 --es-elect --cluster-name some-name
    
    Frontend with postgres
    $ bin/deploy --save-config-name 20200421 --es-ip a.b.c.d --cluster-name some-name
    ```

# Deploy with prebuilt cloud config yml
    ```
    Demo
    $ bin/deploy -n test-demo-prebuilt --use-prebuilt-config 20200421-demo --full-build
   
    ES Node - wait
    $ bin/deploy --save-config-name 20200421 --es-wait --cluster-name some-name

    ES Node - elect
    $ bin/deploy --save-config-name 20200421 --es-elect --cluster-name some-name
    
    Frontend with postgres
    $ bin/deploy --save-config-name 20200421 --es-ip a.b.c.d --cluster-name some-name
    ```

# TBD
## Build encoded AMIs
## Deploy demo
## Deploy cluster

## From remote pg demo
### Deplot a demo with open postgres port
    ```
    export branch_name='ENCD-5216-deploy-demo-pointing-at-pg'
    bin/deploy -b $branch_name -n 5216-pg-open --pg-open --full-build
    ```

### Deploy a demo with open postgres port
    ```
    export branch_name='ENCD-5216-deploy-demo-pointing-at-pg'
    export pg_ip='172.31.20.118'
    # remote postgres ip will be used for --es-ip 'ignored-with-pg-ip'
    bin/deploy -b $branch_name -n 5216-pg-remote --pg-ip $pg_ip --full-build
    ```

## From remote es demo
### Deploy es cluster
    ```
    export branch_name='5212-deploy-demo-pointing-at-es-cluster'
    export cluster_name='5212-demo-es'
    bin/deploy -b $branch_name --cluster-name $cluster_name --es-wait
    # outputs: '--es-ip 172.31.23.141'
    ```

### Deploy a frontend to index the demeo
    ```
    export branch_name='5212-deploy-demo-pointing-at-es-cluster'
    export cluster_name='5212-demo-es'
    export es_ip='172.31.23.141'
    bin/deploy -b $branch_name --cluster-name $cluster_name --es-ip $es_ip
    ```

### Deploy new frontend at es ip with its own db at the current snapshot.
    ```
    export branch_name='5212-deploy-demo-pointing-at-es-cluster'
    export es_ip='172.31.23.141'
    bin/deploy -b $branch_name -n 5121-test-demo --es-ip $es_ip --full-build
    ```
