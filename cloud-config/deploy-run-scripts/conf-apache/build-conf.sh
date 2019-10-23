#!/bin/bash
# #
# This will build the encoded.conf for apache in dest_file location
# - On a demo the encd.install.sh script sets the source and destintion
# - This sript can be tested in the build-conf.sh script directory by running 
#       $./build-conf.sh True 6 or $./build-conf.sh False 3
#  without any args.  Current directory is assumed.
# # 

REGION_INDEX="$1"
APP_WORKERS="$2"
src_dir="$3"
if [ -z "$src_dir" ]; then
    src_dir="./"
fi
dest_file="$4"
if [ -z "$dest_file" ]; then
    dest_file="$src_dir/encoded.conf"
fi


# Top
cat "$src_dir/head.conf" > "$dest_file"
sed "s/APP_WORKERS/$APP_WORKERS/" <  "$src_dir/app.conf" >> "$dest_file"

# indexer processes
cat "$src_dir/indexer-proc.conf" >> "$dest_file"
cat "$src_dir/vis-indexer-proc.conf" >> "$dest_file"
if [ "$REGION_INDEX" == "True" ]; then
    cat "$src_dir/region-indexer-proc.conf" >> "$dest_file"
fi

# Some vars
cat "$src_dir/some-vars.conf" >> "$dest_file"

# indexer directory permissions
cat "$src_dir/indexer-dir-permission.conf" >> "$dest_file"
cat "$src_dir/vis-indexer-dir-permission.conf" >> "$dest_file"
if [ "$REGION_INDEX" == "True" ]; then
    cat "$src_dir/region-indexer-dir-permission.conf" >> "$dest_file"
fi

# the rest
cat "$src_dir/the-rest.conf" >> "$dest_file"
