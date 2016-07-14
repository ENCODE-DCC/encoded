#!/bin/bash
 		aws --profile production s3 ls s3://encode-test-files-upload/
 		if [ $? -ne 0 ]; then
 			echo "ERROR: exit status 1 Cannot list s3 bucket: your keys may be incorrect or you do not have permissions for that bucket."
 			exit
 		fi
 			aws --profile production s3 cp s3://encode-test-files-upload/testDown.jpg .
 		if [ $? -ne 0 ]; then
 			echo "ERROR: exit status 1 Cannot copy test image: your keys may be incorrect or you do not have permissions for that bucket."
 			exit
 		fi 
 			aws --profile production s3 ls s3://encode-test-files-upload/
 			aws --profile production s3 mv testDown.jpg s3://encode-test-files-upload/testUp.jpg
 		if [ $? -ne 0 ]; then
 			 echo "ERROR: exit status 1 Cannot move test image: your keys may be incorrect or you do not have permissions for that bucket."
 		 	exit
 		fi
 			aws --profile production s3 ls s3://encode-test-files-upload/
 			echo "SUCESS: exit status "$? "test Passed."