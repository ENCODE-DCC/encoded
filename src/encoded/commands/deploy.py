
import boto.ec2
import time
import sys

conn = boto.ec2.connect_to_region("us-west-1")

reservation = conn.run_instances(
    'ami-7e37033b',
    instance_type='m3.xlarge',
    security_group_ids=['sg-df30f19b'],
    user_data=open('cloud-config.yml').read(),
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

