from boto.ec2.blockdevicemapping import (
    BlockDeviceMapping,
    BlockDeviceType,
)
import boto.ec2
import boto.exception
import getpass
import re
import subprocess
import sys
import time


def nameify(s):
    name = ''.join(c if c.isalnum() else '-' for c in s.lower()).strip('-')
    return re.subn(r'\-+', '-', name)[0]


def run(wale_s3_prefix, image_id, instance_type, elasticsearch,
        branch=None, name=None, role='demo', profile_name=None):
    if branch is None:
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()

    commit = subprocess.check_output(['git', 'rev-parse', '--short', branch]).decode('utf-8').strip()
    if not subprocess.check_output(['git', 'branch', '-r', '--contains', commit]).strip():
        print("Commit %r not in origin. Did you git push?" % commit)
        sys.exit(1)

    username = getpass.getuser()

    if name is None:
        name = nameify('%s-%s-%s' % (branch, commit, username))
        if elasticsearch == 'yes':
            name ='elasticsearch-' + name

    conn = boto.ec2.connect_to_region("us-west-2", profile_name=profile_name)

    domain = 'production' if profile_name == 'production' else 'instance'

    if any(name == i.tags.get('Name')
           for reservation in conn.get_all_instances()
           for i in reservation.instances
           if i.state != 'terminated'):
        print('An instance already exists with name: %s' % name)
        sys.exit(1)

    bdm = BlockDeviceMapping()
    bdm['/dev/sda1'] = BlockDeviceType(volume_type='gp2', delete_on_termination=True, size=60)
    # Don't attach instance storage so we can support auto recovery
    bdm['/dev/sdb'] = BlockDeviceType(no_device=True)
    bdm['/dev/sdc'] = BlockDeviceType(no_device=True)
    

    if not elasticsearch == 'yes':
        user_data = subprocess.check_output(['git', 'show', commit + ':cloud-config.yml']).decode('utf-8')
        user_data = user_data % {
            'WALE_S3_PREFIX': wale_s3_prefix,
            'COMMIT': commit,
            'ROLE': role,
        }
        security_groups = ['ssh-http-https']
    else:
        user_data = subprocess.check_output(['git', 'show', commit + ':cloud-config-elasticsearch.yml']).decode('utf-8')
        security_groups = ['elasticsearch-https']

    reservation = conn.run_instances(
        image_id=image_id,
        instance_type=instance_type,
        security_groups=security_groups,
        user_data=user_data,
        block_device_map=bdm,
        instance_initiated_shutdown_behavior='terminate',
        instance_profile_name='encoded-instance',
    )

    time.sleep(0.5)  # sleep for a moment to ensure instance exists...
    instance = reservation.instances[0]  # Instance:i-34edd56f
    print('%s.%s.encodedcc.org' % (instance.id, domain))
    instance.add_tags({
        'Name': name,
        'branch': branch,
        'commit': commit,
        'started_by': username,
    })
    print('ssh %s.%s.encodedcc.org' % (name, domain))
    if domain == 'instance':
        print('https://%s.demo.encodedcc.org' % name)

    sys.stdout.write(instance.state)
    while instance.state == 'pending':
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1)
        try:
            instance.update()
        except boto.exception.EC2ResponseError:
            pass
    print('')
    print(instance.state)


def main():
    import argparse

    def hostname(value):
        if value != nameify(value):
            raise argparse.ArgumentTypeError(
                "%r is an invalid hostname, only [a-z0-9] and hyphen allowed." % value)
        return value

    parser = argparse.ArgumentParser(
        description="Deploy ENCODE on AWS",
    )
    parser.add_argument('-b', '--branch', default=None, help="Git branch or tag")
    parser.add_argument('-n', '--name', type=hostname, help="Instance name")
    parser.add_argument('--wale-s3-prefix', default='s3://encoded-backups-prod/production')
    parser.add_argument(
        '--candidate', action='store_const', default='demo', const='candidate', dest='role',
        help="Deploy candidate instance")
    parser.add_argument(
        '--test', action='store_const', default='demo', const='test', dest='role',
        help="Deploy to production AWS")
    parser.add_argument(
        '--image-id', default='ami-1c1eff2f',
        help="ubuntu/images/hvm-ssd/ubuntu-trusty-14.04-amd64-server-20151015")
    parser.add_argument(
        '--instance-type', default='t2.large',
        help="specify 'c4.4xlarge' for faster indexing (you should switch to a smaller "
             "instance afterwards.)")
    parser.add_argument('--profile-name', default=None, help="AWS creds profile")
    parser.add_argument('--elasticsearch', default=None, help="Launch an Elasticsearch instance")
    args = parser.parse_args()

    return run(**vars(args))


if __name__ == '__main__':
    main()
