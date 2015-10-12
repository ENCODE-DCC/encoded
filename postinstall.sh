#!/bin/sh

# Apply patches to installed modules.
for package_name in $(cd node_patches && ls -d *)
do
    for found_package in $(find node_modules -path *node_modules/$package_name -type d)
    do
        for patch_file in $(find node_patches/$package_name -type f)
        do
            echo "Patching $package_name at $found_package with $patch_file"
            patch -p1 -f -i $(pwd)/$patch_file -d $found_package || echo already applied
        done
    done
done
