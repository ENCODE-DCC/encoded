Organization deployment configuration and build files
=====================================================


## Example commands

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
