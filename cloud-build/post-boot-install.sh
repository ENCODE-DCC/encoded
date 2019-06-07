#!/bin/bash
### Run first after cloud init installation
# For general items that did not fit/belong in cloud init
# ubuntu user
# apt deps:
# 	awscli

# Add team ssh public keys from s3
mv /home/ubuntu/.ssh/authorized_keys /home/ubuntu/.ssh/authorized_keys2
aws s3 cp --region=us-west-2 s3://encoded-conf-prod/ssh-keys/demo-authorized_keys /home/ubuntu/.ssh/authorized_keys
