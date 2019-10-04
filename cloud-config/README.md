# Organization deployment configuration and build files
## Directories
    * config-build-files
    * deploy-run-scripts
    * prebuilt-config-yamls


# Primary Deployments
* Development Deployment or Demo: Single instance with front, postgres, es data, es head 
* Elect Cluster: Single instance with frontend and postgres.  5 Node cluster with self elected head node.
* Wait Cluster: Single instance with frontend and postgres.  5 Node cluster with 6th instance for head node.

## Dev Deployment
    * Made       Prebuild: $bin/deploy -n dev-conf --save-config-name 20191002
        # Wrote new config to ./cloud-config/prebuilt-config-yamls/20191002-demo.yml
    * Diff Build/Prebuild: $bin/deploy -n dev-conf --use-prebuilt-config 20191002-demo --diff-configs
    * Deploy     Prebuild: $bin/deploy -n dev-conf --use-prebuilt-config 20191002-demo
    * Deploy        Build: $bin/deploy -n dev-conf


### Elect Cluster
#### Nodes
    * Made       Prebuild: $bin/deploy --cluster-name elect-conf --es-elect --save-config-name 20191002
        # Wrote new config to ./cloud-config/prebuilt-config-yamls/20191002-es-nodes.yml
    * Diff Build/Prebuild: $bin/deploy --cluster-name elect-conf --es-elect --use-prebuilt-config 20191002-es-nodes --diff-configs
    * Deploy     Prebuild: $bin/deploy --cluster-name elect-conf-pre --es-elect --use-prebuilt-config 20191002-es-nodes
    * Deploy        Build: $bin/deploy --cluster-name elect-conf --es-elect 
#### Frontend
    * Made       Prebuild: $bin/deploy --cluster-name elect-conf --save-config-name 20191002
        # Wrote new config to ./cloud-config/prebuilt-config-yamls/20191002-frontend.yml
    * Diff Build/Prebuild: $bin/deploy --cluster-name elect-conf --use-prebuilt-config 20191002-frontend --diff-configs
    * Deploy     Prebuild: $bin/deploy --cluster-name elect-conf-pre --es-ip $HEADNODEIP --use-prebuilt-config 20191002-frontend
    * Deploy        Build: $bin/deploy --cluster-name elect-conf --es-ip $HEADNODEIP
# Deploying frontend
# $ bin/deploy --cluster-name elect-conf-pre --es-ip 172.31.29.3 --use-prebuilt-config 20191002-frontend
Host elect-conf-pre.*
  Hostname i-09c9f0b2e363b7149.instance.encodedcc.org
  # https://elect-conf-pre.demo.encodedcc.org
  # ssh ubuntu@i-09c9f0b2e363b7149.instance.encodedcc.org
# Deploying es-nodes
# $ bin/deploy --cluster-name elect-conf-pre --es-elect --use-prebuilt-config 20191002-es-nodes
Host elect-conf-pre.*
  Hostname i-09eb8ecbe23b9d4bd.instance.encodedcc.org
  # Data Node 0: i-0f88e732ac77e4014
  # Data Node 1: i-04ae1ece8f20f7219
  # Data Node 2: i-05e4302122bb105b1
  # Data Node 3: i-09eb8ecbe23b9d4bd
  # Data Node 4: i-034f0085b7c5a7edd


### Wait Cluster
* Same yaml template as elect cluster but deploy with --wait-data-head argument
#### Nodes: Head node create automatically with data nodes
    * Deploy     Prebuild: $bin/deploy --cluster-name wait-conf-pre --es-wait --use-prebuilt-config 20191002-es-nodes
    * Deploy        Build: $bin/deploy --cluster-name wait-conf --es-wait
#### Frontend
    * Deploy     Prebuild: $bin/deploy --cluster-name wait-conf-pre --es-ip $HEADNODEIP --use-prebuilt-config 20191002-frontend
    * Deploy        Build: $bin/deploy --cluster-name wait-conf --es-ip $HEADNODEIP
# Deploying frontend
# $ bin/deploy --cluster-name wait-conf-pre --es-ip 172.31.16.71 --use-prebuilt-config 20191002-frontend
Host wait-conf-pre.*
  Hostname i-013f40700bc4c7047.instance.encodedcc.org
  # https://wait-conf-pre.demo.encodedcc.org
  # ssh ubuntu@i-013f40700bc4c7047.instance.encodedcc.org
# Deploying es-nodes
# $ bin/deploy --cluster-name wait-conf-pre --es-wait --use-prebuilt-config 20191002-es-nodes
Host wait-conf-pre-dn.*
  Hostname i-048cbcce9f04fa91e.instance.encodedcc.org
  # Data Node 0: i-048cbcce9f04fa91e
  # Data Node 1: i-0e6186984144b39fe
  # Data Node 2: i-01cac4c114a0ed8be
  # Data Node 3: i-0741c08584531ba0d
  # Data Node 4: i-01dacaf711a9f2094
Host wait-conf-pre-dm.*
  Hostname i-0d7ee88e6268d727f.instance.encodedcc.org



# Special Deployments
* RC Cluster Deployment
* Test Cluster Deployment
* Prod Cluster Deployment
