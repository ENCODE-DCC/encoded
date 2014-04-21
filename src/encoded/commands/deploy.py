from boto.ec2.blockdevicemapping import (
    BlockDeviceMapping,
    BlockDeviceType,
)
import boto.ec2
import time
import sys
import os


def run(branch, instance_name=None, persistent=False):
    if instance_name is None:
        # Ideally we'd use the commit sha here, but only the instance knows that...
        instance_name = 'encoded/%s' % branch

    conn = boto.ec2.connect_to_region("us-west-1")
    bdm = BlockDeviceMapping()
    if persistent:
        bdm['/dev/xvdf'] = BlockDeviceType(snapshot_id='snap-9bdfcd91', delete_on_termination=True)
        bdm['/dev/xvdg'] = BlockDeviceType(snapshot_id='snap-9bdfcd91', delete_on_termination=True)
    else:
        bdm['/dev/xvdf'] = BlockDeviceType(ephemeral_name='ephemeral0')
        bdm['/dev/xvdg'] = BlockDeviceType(ephemeral_name='ephemeral1')

    user_data = open('cloud-config.yml').read()
    user_data = user_data % {
        'AWS_ID': os.environ["S3_READ_ID"],
        'AWS_KEY': os.environ["S3_READ_KEY"],
        'AWS_SERVER': os.environ["S3_SERVER"],
        'BRANCH': branch,
    }

    reservation = conn.run_instances(
        'ami-f64f77b3',  # ubuntu/images/hvm/ubuntu-trusty-14.04-amd64-server-20140416.1
        instance_type='m3.xlarge',
        security_group_ids=['sg-df30f19b'],
        user_data=user_data,
        block_device_map=bdm,
        instance_initiated_shutdown_behavior='terminate',
    )

    instance = reservation.instances[0]  # Instance:i-34edd56f
    instance.add_tag('Name', instance_name)
    instance.add_tag('branch', branch)
    print instance
    print instance.state,

    while instance.state == 'pending':
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1)
        instance.update()

    print
    print instance.state

    print instance.public_dns_name  # u'ec2-54-219-26-167.us-west-1.compute.amazonaws.com'


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Deploy ENCODE on AWS",
    )
    parser.add_argument('-b', '--branch', default='master', help="Git branch or tag")
    parser.add_argument('-n', '--name', help="Instance name")
    parser.add_argument('--persistent', action='store_true', help="User persistent (ebs) volumes")
    args = parser.parse_args()

    return run(args.branch, args.name, args.persistent)


if __name__ == '__main__':
    main()
