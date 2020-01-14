#!/bin/bash
# Setup elasticsearch data node config
# root user
# apt deps:
#   java
#   elasticsearch with apt_source and key
echo -e "\n**** ENCDINSTALL $(basename $0) ****"
CLUSTER_NAME="$1"
JVM_GIGS="$2"
ES_OPT_FILENAME="$3"

opts_src='/home/ubuntu/encoded/cloud-config/deploy-run-scripts/conf-es'
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


# jvm options
jvm_opts_filename='jvm.options'
jvm_xms='-Xms'"$JVM_GIGS"'g'
jvm_xmx='-Xmx'"$JVM_GIGS"'g'
append_with_user "$jvm_xms" ubuntu "$opts_src/$jvm_opts_filename"
append_with_user "$jvm_xmx" ubuntu "$opts_src/$jvm_opts_filename"
copy_with_permission "$opts_src/$jvm_opts_filename" "$opts_dest/$jvm_opts_filename"

# elasticsearch options
es_opts_filename="$ES_OPT_FILENAME"
if [ "$CLUSTER_NAME" == 'NONE' ]; then
    echo 'Not a elasticsearch cluster'
else
    # Only append a cluster name if it is not 'NONE'
    # like single demos do not have cluster names
    cluster_name="cluster.name: $CLUSTER_NAME"
    append_with_user "$cluster_name" ubuntu "$opts_src/$es_opts_filename"
fi
copy_with_permission "$opts_src/$es_opts_filename" "$opts_dest/elasticsearch.yml"

# Setup/Restart
update-rc.d elasticsearch defaults
sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install discovery-ec2
service elasticsearch restart
