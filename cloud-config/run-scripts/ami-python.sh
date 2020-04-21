#!/bin/bash
# In order to use python3.7 in Ubuntu 18 we need to compile mod_wsgi hence python 3.7 manually
# Links:
# - https://medium.com/@garethbjohnson/serve-python-3-7-with-mod-wsgi-on-ubuntu-16-d9c7ab79e03a
echo -e "\n$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
PYV="$1"

# Create python application dir
sudo mkdir "$ENCD_PY3_DIR"
sudo chown ubuntu:ubuntu "$ENCD_PY3_DIR"

# Check for manual 3.7 skip
if [ "$PYV" == 'PY36' ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Flag: Install python3.6"
    sudo apt install -y python3-dev python3-venv
    # Hack in sym link and bin dir and path
    mkdir "$ENCD_PY3_DIR/bin"
    ln -s /usr/bin/python3 "$ENCD_PY3_DIR/bin/python3.7"
    exit 0
fi

# Install 3.7 manually
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Manual python3.7 install"

# Used to speed up 'make'
# - Adding a few more is recommeneded
NUM_CPUS=$(cat /proc/cpuinfo | grep processor | wc -l)
NUM_CPUS=$((NUM_CPUS+3))

# Python Install
BUILD_DIR='/opt/Python_Build'
sudo mkdir "$BUILD_DIR"
sudo chown ubuntu:ubuntu "$BUILD_DIR"

TAR_URL='https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tgz'
TAR_URL_OUT="$BUILD_DIR/Python.tgz"
TAR_BUILD="$(echo "$TAR_URL_OUT" | cut -f 1 -d '.')"
wget "$TAR_URL" -O "$TAR_URL_OUT"
tar xzf "$TAR_URL_OUT" --one-top-level="$TAR_BUILD" --strip-components 1

cd $TAR_BUILD
./configure --enable-shared --enable-optimizations --prefix="$ENCD_PY3_DIR"
time make -j $NUM_CPUS
time make -j $NUM_CPUS altinstall

# Build mod_wsgi if python3 install worked
if [ -f "$ENCD_PY3_PATH" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) mod_wsgi"
    echo "/opt/python/lib" | sudo -u root tee -a /etc/ld.so.conf
    sudo /sbin/ldconfig -v
    BUILD_DIR='/opt/Mod_Wsgi_Build'
    sudo mkdir "$BUILD_DIR"
    sudo chown ubuntu:ubuntu "$BUILD_DIR"

    TAR_URL='https://github.com/GrahamDumpleton/mod_wsgi/archive/4.6.5.tar.gz'
    TAR_URL_OUT="$BUILD_DIR/mod_wsgi.tar.gz"
    TAR_BUILD="$(echo "$TAR_URL_OUT" | cut -f 1 -d '.')"
    wget $TAR_URL -O "$TAR_URL_OUT"
    tar xzf "$TAR_URL_OUT" --one-top-level="$TAR_BUILD" --strip-components 1

    cd $TAR_BUILD
    ./configure --with-python="$ENCD_PY3_PATH"
    time make -j $NUM_CPUS
    time sudo make -j $NUM_CPUS install
else
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: No bin/python"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
