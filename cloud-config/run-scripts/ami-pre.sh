#!/bin/bash
### Run first after cloud init installation
echo -e "\n$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
ADD_PG_ES_AWS_KEYS=1
if [ "$ENCD_BUILD_TYPE" == 'encd-demo-build' ] || [ "$ENCD_BUILD_TYPE" == 'encd-frontend-build' ] || [ "$ENCD_BUILD_TYPE" == 'encd-demo-no-es-build' ]; then
    # Elasticsearch nodes(encd-es-build) do not need aws keys
    ADD_PG_ES_AWS_KEYS=0
fi

# Add team ssh public keys from s3
auth_keys_file='/home/ubuntu/.ssh/authorized_keys'
auth_keys_file2='/home/ubuntu/.ssh/authorized_keys2'
mv "$auth_keys_file" "$auth_keys_file2"
aws s3 cp --region=us-west-2 $ENCD_S3_AUTH_KEYS "$auth_keys_file"
if [ ! -f "$auth_keys_file" ] || [ ! -f "$auth_keys_file2" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: ssh auth keys"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi

if [ $ADD_PG_ES_AWS_KEYS -eq 0 ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Set PG/ENCD aws keys ENCD_BUILD_TYPE=$ENCD_BUILD_TYPE"
    # Downlaod postgres demo aws keys
    pg_keys_dir='/home/ubuntu/pg-aws-keys'
    mkdir "$pg_keys_dir"
    aws s3 cp --region=us-west-2 --recursive s3://encoded-conf-prod/pg-aws-keys "$pg_keys_dir"
    if [ ! -f "$pg_keys_dir/credentials" ]; then
        echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: ubuntu home pg aws creds"
        # Build has failed
        touch "$encd_failed_flag"
        exit 1
    fi

    # Downlaod encoded demo aws keys
    encd_keys_dir=/home/ubuntu/encd-aws-keys
    mkdir "$encd_keys_dir"
    aws s3 cp --region=us-west-2 --recursive s3://encoded-conf-prod/encd-aws-keys "$encd_keys_dir"
    if [ ! -f "$encd_keys_dir/credentials" ]; then
        echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: ubuntu home encd aws creds"
        # Build has failed
        touch "$encd_failed_flag"
        exit 1
    fi
else
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) Skipping PG/ENCD aws keys.  Only for es nodes"
fi
