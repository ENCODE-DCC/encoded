
import boto.ec2
import time
import sys
import os

conn = boto.ec2.connect_to_region("us-west-1")

user_data = open('cloud-config.yml').read()
user_data=user_data % {
    'AWS_ID': os.environ["S3_READ_ID"],
    'AWS_KEY': os.environ["S3_READ_KEY"],
    'AWS_SERVER': os.environ["S3_SERVER"],
}

# Use 'ami-b698a9f3' - ubuntu/images/ebs/ubuntu-saucy-13.10-amd64-server-20131204
reservation = conn.run_instances(
    'ami-b698a9f3',
    instance_type='m3.xlarge',
    security_group_ids=['sg-df30f19b'],
    user_data=user_data,
)

instance = reservation.instances[0] # Instance:i-34edd56f
print instance
print instance.state,

while instance.state == 'pending':
    sys.stdout.write('.')
    sys.stdout.flush()
    time.sleep(1)
    instance.update()

print
print instance.state

print instance.public_dns_name # u'ec2-54-219-26-167.us-west-1.compute.amazonaws.com'
