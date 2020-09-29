#!/bin/bash
## Moves apache conf from repo location to sites-available
# 
# 000-encoded-default.conf
# 111-indexer-primary.conf
# 222-indexer-vis.conf
# 333-indexer-region.conf
# 666-encoded-app.conf
#
## 
src_dir='/home/ubuntu/encoded/cloud-config/configs/apache'
dest_dir='/etc/apache2/sites-available'

site_arr=('000-encoded-default.conf' '111-indexer-primary.conf' '222-indexer-vis.conf' '333-indexer-region.conf')
for filename in ${site_arr[@]}; do
    if [ -f "$dest_dir/$filename" ]; then
        rm "$dest_dir/$filename"
    fi
    cp "$src_dir/$filename" "$dest_dir/$filename"
done

filename='666-encoded-app.conf'
if [ -f "$dest_dir/$filename" ]; then
    rm "$dest_dir/$filename"
fi
sed "s/APP_WORKERS/$ENCD_APP_WORKERS/" <  "$src_dir/$filename" >> "$dest_dir/$filename"
