#!/bin/bash
# Oracle Java 11 installation
echo -e "\n$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
# Manually install java
sudo -u ubuntu aws s3 cp --region=us-east-1 --recursive s3://kce-conf-prod/encd-tars ~ubuntu/encd-tars
sudo mkdir -p /usr/lib/jvm
sudo chmod 777 /usr/lib/jvm
sudo tar -xzvf /home/ubuntu/encd-tars/jdk-11.0.3_linux-x64_bin.tar.gz --directory /usr/lib/jvm/
sudo chmod 755 /usr/lib/jvm
sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk-11.0.3/bin/java 100
java_version="$(java --version | head -n1)" && echo $java_version
if [ ! "$java_version" == "java 11.0.3 2019-04-16 LTS" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: Wrong java versions '$java_version'"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
