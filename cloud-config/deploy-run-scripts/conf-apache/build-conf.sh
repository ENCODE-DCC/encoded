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
#    $ cd encoded/cloud-config/deploy-run-scripts/conf-apache
#    $ ./build-conf.sh False 6 ./ ./test-demo-encoded.conf
#    $ diff demo-encoded.conf test-build-encoded.conf
#    $ ./build-conf.sh True 6 ./ ./test-prod-encoded.conf
#    $ diff prod-encoded.conf test-build-encoded.conf
#
#  - Updating the prebuilt conf files in the repo
#    $ cd encoded/cloud-config/deploy-run-scripts/conf-apache
#    $ ./build-conf.sh False 6 ./ ./demo-encoded.conf
#    $ ./build-conf.sh True 6 ./ ./prod-encoded.conf
#
#  - Updating conf on live demo to turn region indexer on
#    $ cd ~/encoded/cloud-config/deploy-run-scripts/conf-apache
#    $ sudo -u root ./build-conf.sh True 6 ./ /etc/apache2/sites-available/encoded.conf
#    $ sudo serice apache2 restart && tail -f /var/log/apache2/error.log
#
# Use Case with cloud-init in encoded/cloud-config/deploy-run-scripts/app-encd.sh
#  export a2conf_src_dir="/srv/encoded/cloud-config/deploy-run-scripts/conf-apache"
#  export a2conf_dest_file='/etc/apache2/sites-available/encoded.conf'
#  export ENCD_REGION_INDEX=False
#  export ENCD_APP_WORKERS=6
#  sudo -u root "$a2conf_src_dir/build-conf.sh" "$ENCD_REGION_INDEX" "$ENCD_APP_WORKERS" "$a2conf_src_dir" "$a2conf_dest_file"
#
## 


REGION_INDEX=
if [ "$1" == 'True' ] || [ "$1" == 'False' ]; then
    REGION_INDEX="$1"
else
    echo -e "\nFirst arg is 'True' or 'False' to toggle region indexer conf."
    exit 1
fi

APP_WORKERS=
num_pattern='^[1-9]{1,2}$'
if [[ $2 =~ $num_pattern ]]; then
    APP_WORKERS="$2"
else
    echo -e "\nSecond arg is number of apps running, one or two digit integer."
    exit 1
fi

src_dir=
if [ -d "$3" ]; then
    src_dir="$3"
else
    echo -e "\nThird arg source directory of conf parts."
    exit 1
fi

dest_path=
if [ -z "$4" ]; then
    echo -e "\nFourth arg is the destination for the encoded.conf."
    exit 1
else
    dest_path="$4"
fi


# Top
cat "$src_dir/head.conf" > "$dest_path"
sed "s/APP_WORKERS/$APP_WORKERS/" <  "$src_dir/app.conf" >> "$dest_path"

# indexer processes
cat "$src_dir/indexer-proc.conf" >> "$dest_path"
cat "$src_dir/vis-indexer-proc.conf" >> "$dest_path"
if [ "$REGION_INDEX" == "True" ]; then
    cat "$src_dir/region-indexer-proc.conf" >> "$dest_path"
fi

# Some vars
cat "$src_dir/some-vars.conf" >> "$dest_path"

# indexer directory permissions
# encd-demo-no-es-build does not have indexing. REGION_INDEX already defaulted to false.
if [ ! "$ENCD_BUILD_TYPE" == 'encd-demo-no-es-build' ]; then
    cat "$src_dir/indexer-dir-permission.conf" >> "$dest_path"
    cat "$src_dir/vis-indexer-dir-permission.conf" >> "$dest_path"
fi
if [ "$REGION_INDEX" == "True" ]; then
    cat "$src_dir/region-indexer-dir-permission.conf" >> "$dest_path"
fi

# the rest
cat "$src_dir/the-rest.conf" >> "$dest_path"
echo "Conf built: $dest_path"
