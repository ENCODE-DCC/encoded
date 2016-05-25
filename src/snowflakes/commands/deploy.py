import boto3
import getpass
import re
import subprocess
import sys


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
            name = 'elasticsearch-' + name

    session = boto3.Session(region_name='us-west-2', profile_name=profile_name)
    ec2 = session.resource('ec2')

    domain = 'production' if profile_name == 'production' else 'instance'

    if any(ec2.instances.filter(
            Filters=[
                {'Name': 'tag:Name', 'Values': [name]},
                {'Name': 'instance-state-name',
                 'Values': ['pending', 'running', 'stopping', 'stopped']},
            ])):
        print('An instance already exists with name: %s' % name)
        sys.exit(1)

    bdm = [
        {
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'VolumeSize': 120,
                'VolumeType': 'gp2',
                'DeleteOnTermination': True
            }
        },
        {
            'DeviceName': '/dev/sdb',
            'NoDevice': "",
        },
        {
            'DeviceName': '/dev/sdc',
            'NoDevice': "",
        },
    ]

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

    reservation = ec2.create_instances(
        ImageId=image_id,
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        SecurityGroups=security_groups,
        UserData=user_data,
        BlockDeviceMappings=bdm,
        InstanceInitiatedShutdownBehavior='terminate',
        IamInstanceProfile={
            "Name": 'snowflake-instance',
        }
    )

    instance = reservation[0]  # Instance:i-34edd56f
    print('%s.%s.snowflake.org' % (instance.id, domain))
    instance.wait_until_exists()
    instance.create_tags(Tags=[
        {'Key': 'Name', 'Value': name},
        {'Key': 'branch', 'Value': branch},
        {'Key': 'commit', 'Value': commit},
        {'Key': 'started_by', 'Value': username},
    ])
    print('ssh %s.%s.snowflake.org' % (name, domain))
    if domain == 'instance':
        print('https://%s.demo.snowflake.org' % name)

    print('pending...')
    instance.wait_until_running()
    print(instance.state['Name'])


def main():
    import argparse

    def hostname(value):
        if value != nameify(value):
            raise argparse.ArgumentTypeError(
                "%r is an invalid hostname, only [a-z0-9] and hyphen allowed." % value)
        return value

    parser = argparse.ArgumentParser(
        description="Deploy SNOWFLAKE on AWS",
    )
    parser.add_argument('-b', '--branch', default=None, help="Git branch or tag")
    parser.add_argument('-n', '--name', type=hostname, help="Instance name")
    parser.add_argument('--wale-s3-prefix', default='s3://snowflake-backups-prod/production')
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
        '--instance-type', default='c4.4xlarge',
        help="(defualts toc4.4xlarge for indexing) Switch to a smaller instance afterwards"
        "(m4.xlarge or c4.xlarge)")
    parser.add_argument('--profile-name', default=None, help="AWS creds profile")
    parser.add_argument('--elasticsearch', default=None, help="Launch an Elasticsearch instance")
    args = parser.parse_args()

    return run(**vars(args))


if __name__ == '__main__':
    main()
