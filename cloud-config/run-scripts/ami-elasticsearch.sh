#!/bin/bash
# Setup elasticsearch data node config
# - should not be called from frontend build
echo -e "\n$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi

# Check if full build and set do install flag
if [ "$ENCD_FULL_BUILD" == 'True' ]; then
    touch "$encd_do_install_flag"
fi
# Normal builds es is not installed/configured on the ami
if [ "$ENCD_BUILD_TYPE" == 'es-nodes' ]; then
    if [ ! -f "$encd_do_install_flag" ]; then
        echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Skipping ES AMI build. Set do install flag"
        # For es builds we set the do install flag here since this is the main app
        # We could have alternativily created an app-wrapper.sh for elasticsearch
        touch "$encd_do_install_flag"
        exit 0
    fi
fi
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
opts_src="$ENCD_CC_DIR/configs/elasticsearch"
opts_dest='/etc/elasticsearch'

function copy_with_permission {
    src_file="$1"
    dest_file="$2"
    sudo -u root cp "$src_file" "$dest_file"
    sudo -u root chown root:elasticsearch "$dest_file"
}

function append_with_user {
  line="$1"
  user="$2"
  dest="$3"
  echo "$line" | sudo -u $user tee -a $dest
}


# Initial ES install on demos and es nodes
# jvm options
jvm_opts_filename='jvm.options'
jvm_xms='-Xms'"$ENCD_JVM_GIGS"'g'
jvm_xmx='-Xmx'"$ENCD_JVM_GIGS"'g'
append_with_user "$jvm_xms" ubuntu "$opts_src/$jvm_opts_filename"
append_with_user "$jvm_xmx" ubuntu "$opts_src/$jvm_opts_filename"
copy_with_permission "$opts_src/$jvm_opts_filename" "$opts_dest/$jvm_opts_filename"

# elasticsearch options
es_opts_filename="$ENCD_ES_OPT_FILENAME"
if [ "$ENCD_CLUSTER_NAME" == 'NONE' ]; then
    echo 'Not a elasticsearch cluster'
else
    # Only append a cluster name if it is not 'NONE'
    # like single demos do not have cluster names
    cluster_name="cluster.name: $ENCD_CLUSTER_NAME"
    append_with_user "$cluster_name" ubuntu "$opts_src/$es_opts_filename"
fi
if [ "$ENCD_PG_OPEN" == 'true' ]; then
    # Open postgres has open elasticsearch
    network_host='network.host: 0.0.0.0'
    append_with_user "$network_host" ubuntu "$opts_src/$es_opts_filename"
    transport_tcp_port='transport.tcp.port: 9299'
    append_with_user "$transport_tcp_port" ubuntu "$opts_src/$es_opts_filename"
fi
copy_with_permission "$opts_src/$es_opts_filename" "$opts_dest/elasticsearch.yml"

# Install discovery for clusters, maybe only needed for clusters
sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install discovery-ec2
# Add es service and start
sudo /bin/systemctl enable elasticsearch.service
sudo systemctl start elasticsearch.service
if [ $? -gt 0 ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: elasticseach service"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
if [ "$ENCD_BUILD_TYPE" == 'es-nodes' ]; then
    # For es builds we set the is installed flag here since this is the main app
    # We could have alternativily created an app-wrapper.sh for elasticsearch
    touch "$encd_is_installed_flag"
fi
