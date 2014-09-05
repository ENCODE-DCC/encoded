from boto.ec2.blockdevicemapping import (
    BlockDeviceMapping,
    BlockDeviceType,
)
import boto.ec2
import getpass
import time
import subprocess
import sys


def run(wale_s3_prefix, branch=None, name=None, persistent=False):
    if branch is None:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()

    commit = subprocess.check_output(['git', 'rev-parse', '--short', branch]).strip()
    if not subprocess.check_output(['git', 'branch', '-r', '--contains', commit]).strip():
        print("Commit %r not in origin. Did you git push?" % commit)
        sys.exit(1)

    username = getpass.getuser()

    if name is None:
        name = 'encoded/%s@%s by %s' % (branch, commit, username)

    conn = boto.ec2.connect_to_region("us-west-2")
    bdm = BlockDeviceMapping()
    if persistent:
        bdm['/dev/xvdf'] = BlockDeviceType(snapshot_id='snap-8f90c779', delete_on_termination=True)
        bdm['/dev/xvdg'] = BlockDeviceType(snapshot_id='snap-8f90c779', delete_on_termination=True)
    else:
        bdm['/dev/xvdf'] = BlockDeviceType(ephemeral_name='ephemeral0')
        bdm['/dev/xvdg'] = BlockDeviceType(ephemeral_name='ephemeral1')

    user_data = subprocess.check_output(['git', 'show', commit + ':cloud-config.yml'])
    user_data = user_data % {
        'WALE_S3_PREFIX': wale_s3_prefix,
        'COMMIT': commit,
    }

    reservation = conn.run_instances(
        'ami-199add29',  # ubuntu/images/hvm/ubuntu-trusty-14.04-amd64-server-20140829
        instance_type='m3.xlarge',
        security_groups=['ssh-http-https'],
        user_data=user_data,
        block_device_map=bdm,
        instance_initiated_shutdown_behavior='terminate',
        instance_profile_name='demo-instance',
    )

    instance = reservation.instances[0]  # Instance:i-34edd56f
    instance.add_tag('Name', name)
    instance.add_tag('commit', commit)
    instance.add_tag('started_by', username)
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
    parser.add_argument('-b', '--branch', default=None, help="Git branch or tag")
    parser.add_argument('-n', '--name', help="Instance name")
    parser.add_argument('--persistent', action='store_true', help="User persistent (ebs) volumes")
    parser.add_argument('--wale-s3-prefix', default='s3://encoded-backups/production')
    args = parser.parse_args()

    return run(**vars(args))


if __name__ == '__main__':
    main()
