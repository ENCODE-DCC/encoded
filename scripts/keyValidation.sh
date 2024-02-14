#!/bin/bash
if [ $1 == "demo" ]; then
    bucket="encode-test-files-upload-demo"
elif [ $1 == "prod" ]; then
    bucket="encode-test-files-upload"
else
    echo "not a valid argument: requires "demo" or "prod""
    exit
fi

aws --profile encoded-files-upload s3 ls s3://$bucket/
if [ $? -ne 0 ]; then
    echo "ERROR: exit status 1 Cannot list s3 bucket: your keys may be incorrect or you do not have permissions for that bucket."
    exit
fi

aws --profile encoded-files-upload s3 cp s3://$bucket/testDown.jpg .
if [ $? -ne 0 ]; then
    echo "ERROR: exit status 1 Cannot copy test image: your keys may be incorrect or you do not have permissions for that bucket."
    exit
fi

aws --profile encoded-files-upload s3 ls s3://$bucket/
aws --profile encoded-files-upload s3 mv testDown.jpg s3://$bucket/testUp.jpg
if [ $? -ne 0 ]; then
    echo "ERROR: exit status 1 Cannot move test image: your keys may be incorrect or you do not have permissions for that bucket."
    exit
fi
aws --profile encoded-files-upload s3 ls s3://$bucket/
echo "SUCESS: exit status "$? "test Passed."
