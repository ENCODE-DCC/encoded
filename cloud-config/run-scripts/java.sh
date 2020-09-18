#!/bin/bash
echo -e "\n$(basename $0) Running"
sudo -u ubuntu aws s3 cp --region=us-west-2 --recursive s3://encoded-conf-prod/encd-tars ~ubuntu/encd-tars
sudo mkdir -p /usr/lib/jvm
sudo chmod 777 /usr/lib/jvm
sudo tar -xzvf /home/ubuntu/encd-tars/jdk-11.0.3_linux-x64_bin.tar.gz --directory /usr/lib/jvm/
sudo chmod 755 /usr/lib/jvm
sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk-11.0.3/bin/java 100
java_version="$(java --version | head -n1)" && echo $java_version
echo "ENCD: Java version '$java_version'"
