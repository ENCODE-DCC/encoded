#!/bin/bash
### Run first after cloud init installation
# For general items that did not fit/belong in cloud init
# ubuntu user
# apt deps:
# 	awscli
echo -e "\n**** ENCDINSTALL $(basename $0) ****"
S3_AUTH_KEYS=$1

# Add team ssh public keys from s3
mv /home/ubuntu/.ssh/authorized_keys /home/ubuntu/.ssh/authorized_keys2
aws s3 cp --region=us-west-2 $S3_AUTH_KEYS /home/ubuntu/.ssh/authorized_keys
# Downlaod postgres demo aws keys
mkdir /home/ubuntu/pg-aws-keys
aws s3 cp --region=us-west-2 --recursive s3://encoded-conf-prod/pg-aws-keys /home/ubuntu/pg-aws-keys
# Downlaod encoded demo aws keys
mkdir /home/ubuntu/encd-aws-keys
aws s3 cp --region=us-west-2 --recursive s3://encoded-conf-prod/encd-aws-keys /home/ubuntu/encd-aws-keys
