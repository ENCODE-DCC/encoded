#!/bin/bash
## Build the encoded.conf for apache in given a location
# 
# Arguments: 
#  1: Source directory for the configuration files
#  2: Destination to save encoded.conf
#
#  - Updating conf on live demo
#    $ cat /etc/environment # to check variables
#    $ cd ~/encoded/cloud-config/configs/apache
#    $ sudo -u root ./build-conf.sh ./ /etc/apache2/sites-available/encoded.conf
#    $ sudo service apache2 restart && tail -f /var/log/apache2/error.log
#
# Use Case with cloud-init in encoded/cloud-config/configs/app-encd.sh
#  export a2conf_src_dir="/srv/encoded/cloud-config/configs/apache"
#  export a2conf_dest_file='/etc/apache2/sites-available/encoded.conf'
#  export encd_index_region=False
#  export encd_app_workers=6
#  sudo -u root "$a2conf_src_dir/build-conf.sh" "$a2conf_src_dir" "$a2conf_dest_file"
#
## 


src_dir=
if [ -d "$1" ]; then
    src_dir="$1"
else
    echo -e "\nFirst arg source directory of conf parts."
    exit 1
fi

dest_path=
if [ -z "$2" ]; then
    echo -e "\nSecond arg is the destination for the encoded.conf."
    exit 1
else
    dest_path="$2"
fi


# Top
cat "$src_dir/head.conf" > "$dest_path"
sed "s/APP_WORKERS/$encd_app_workers/" <  "$src_dir/app.conf" >> "$dest_path"

# indexer processes
if [ "$encd_index_primary" == 'true' ]; then
        cat "$src_dir/indexer-proc.conf" >> "$dest_path"
fi
if [ "$encd_index_vis" == 'true' ]; then
    cat "$src_dir/vis-indexer-proc.conf" >> "$dest_path"
fi
if [ "$encd_index_region" == 'true' ]; then
    cat "$src_dir/region-indexer-proc.conf" >> "$dest_path"
fi

# Some vars
cat "$src_dir/some-vars.conf" >> "$dest_path"

# indexer directory permissions
if [ "$encd_index_primary" == 'true' ]; then
        cat "$src_dir/indexer-dir-permission.conf" >> "$dest_path"
fi
if [ "$encd_index_vis" == 'true' ]; then
    cat "$src_dir/vis-indexer-dir-permission.conf" >> "$dest_path"
fi
if [ "$encd_index_region" == 'true' ]; then
    cat "$src_dir/region-indexer-dir-permission.conf" >> "$dest_path"
fi

# the rest
cat "$src_dir/the-rest.conf" >> "$dest_path"
echo "Conf built: $dest_path"
