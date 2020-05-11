#!/bin/bash
## Build the encoded.conf for apache in given a location
# 
# Arguments: 
#  1: Add region indexer conf: 'True' or 'False'
#  2: Number of encoded apps to run: 6 is typical
#  3: Destination to save encoded.conf
#
#
# Examples:
#  - Testing the script on OSX 
#    $ cd encoded/cloud-config/configs/apache
#    $ ./build-conf.sh False 6 ./ ./test-demo-encoded.conf
#    $ diff demo-encoded.conf test-build-encoded.conf
#    $ ./build-conf.sh True 6 ./ ./test-prod-encoded.conf
#    $ diff prod-encoded.conf test-build-encoded.conf
#
#  - Updating the prebuilt conf files in the repo
#    $ cd encoded/cloud-config/configs/apache
#    $ ./build-conf.sh False 6 ./ ./demo-encoded.conf
#    $ ./build-conf.sh True 6 ./ ./prod-encoded.conf
#
#  - Updating conf on live demo to turn region indexer on
#    $ cd ~/encoded/cloud-config/configs/apache
#    $ sudo -u root ./build-conf.sh True 6 ./ /etc/apache2/sites-available/encoded.conf
#    $ sudo serice apache2 restart && tail -f /var/log/apache2/error.log
#
# Use Case with cloud-init in encoded/cloud-config/configs/app-encd.sh
#  export a2conf_src_dir="/srv/encoded/cloud-config/configs/apache"
#  export a2conf_dest_file='/etc/apache2/sites-available/encoded.conf'
#  export ENCD_REGION_INDEX=False
#  export ENCD_APP_WORKERS=6
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
sed "s/APP_WORKERS/$ENCD_APP_WORKERS/" <  "$src_dir/app.conf" >> "$dest_path"

# indexer processes
if [ "$ENCD_INDEX_PRIMARY" == 'true' ]; then
        cat "$src_dir/indexer-proc.conf" >> "$dest_path"
else
    if [ "$ENCD_INDEX_VIS" == 'true' ]; then
        cat "$src_dir/vis-indexer-proc.conf" >> "$dest_path"
    fi
    if [ "$ENCD_INDEX_REGION" == 'true' ]; then
        cat "$src_dir/region-indexer-proc.conf" >> "$dest_path"
    fi
fi

# Some vars
cat "$src_dir/some-vars.conf" >> "$dest_path"

# indexer directory permissions
if [ "$ENCD_INDEX_PRIMARY" == 'true' ]; then
        cat "$src_dir/indexer-dir-permission.conf" >> "$dest_path"
else
    if [ "$ENCD_INDEX_VIS" == 'true' ]; then
        cat "$src_dir/vis-indexer-dir-permission.conf" >> "$dest_path"
    fi
    if [ "$ENCD_INDEX_REGION" == 'true' ]; then
        cat "$src_dir/region-indexer-dir-permission.conf" >> "$dest_path"
    fi
fi

# the rest
cat "$src_dir/the-rest.conf" >> "$dest_path"
echo "Conf built: $dest_path"
