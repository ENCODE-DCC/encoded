
#import logging

#DOCTYPE = 'basic'

#EPILOG = __doc__

#log = logging.getLogger(__name__)

def run(branch):
    import boto.ec2
    import time
    import sys
    import os
    instance_name = 'encoded/%s' % branch

    conn = boto.ec2.connect_to_region("us-west-1")
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    bdm['/dev/sdf'] = boto.ec2.blockdevicemapping.BlockDeviceType(snapshot_id='snap-9bdfcd91', delete_on_termination=True)
    bdm['/dev/sdg'] = boto.ec2.blockdevicemapping.BlockDeviceType(snapshot_id='snap-9bdfcd91', delete_on_termination=True)

    user_data = open('cloud-config.yml').read()
    user_data=user_data % {
        'AWS_ID': os.environ["S3_READ_ID"],
        'AWS_KEY': os.environ["S3_READ_KEY"],
        'AWS_SERVER': os.environ["S3_SERVER"],
        'BRANCH': branch,
    }

    # Use 'ami-b698a9f3' - ubuntu/images/ebs/ubuntu-saucy-13.10-amd64-server-20131204
    reservation = conn.run_instances(
        'ami-b698a9f3',
        instance_type='m3.xlarge',
        security_group_ids=['sg-df30f19b'],
        user_data=user_data,
        block_device_map=bdm,
        instance_initiated_shutdown_behavior='terminate',
    )

    instance = reservation.instances[0] # Instance:i-34edd56f
    instance.add_tag('Name', instance_name) 
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


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Deploy ENCODE on AWS", 
    )
    parser.add_argument('-b', '--branch', default='master', help="Git branch or tag")
    args = parser.parse_args()

    return run(args.branch)


if __name__ == '__main__':
    main()
