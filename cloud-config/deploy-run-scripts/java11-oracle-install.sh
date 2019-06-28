#!/bin/bash
# Oracle Java 11 installation 
# ubuntu user
# apt deps:

# Manually install java
sudo -u ubuntu aws s3 cp --region=us-west-2 --recursive s3://encoded-conf-prod/.aws ~ubuntu/.aws
sudo mkdir -p /usr/lib/jvm
sudo chmod 777 /usr/lib/jvm
sudo tar -xzvf /home/ubuntu/.aws/jdk-11.0.3_linux-x64_bin.tar.gz --directory /usr/lib/jvm/
sudo -u ubuntu rm -r /home/ubuntu/.aws
sudo chmod 755 /usr/lib/jvm
sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk-11.0.3/bin/java 100
