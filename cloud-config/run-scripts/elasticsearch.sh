#!/bin/bash
echo -e "\n$(basename $0) Running"

# Script Below
opts_src="$encd_cc_dir/configs/elasticsearch"
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
jvm_xms='-Xms'"$encd_es_jvm_gigs"'g'
jvm_xmx='-Xmx'"$encd_es_jvm_gigs"'g'
append_with_user "$jvm_xms" ubuntu "$opts_src/$jvm_opts_filename"
append_with_user "$jvm_xmx" ubuntu "$opts_src/$jvm_opts_filename"
copy_with_permission "$opts_src/$jvm_opts_filename" "$opts_dest/$jvm_opts_filename"

# elasticsearch options
es_opts_filename="$encd_es_opt_filename"
copy_with_permission "$opts_src/$es_opts_filename" "$opts_dest/elasticsearch.yml"

# Install discovery for clusters, maybe only needed for clusters
sudo /usr/share/elasticsearch/bin/elasticsearch-plugin install discovery-ec2
# Add es service and start
sudo /bin/systemctl enable elasticsearch.service
sudo systemctl start elasticsearch.service
