import boto3
import getpass
import re
import subprocess
import sys


BDM = [
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


def nameify(s):
    name = ''.join(c if c.isalnum() else '-' for c in s.lower()).strip('-')
    return re.subn(r'\-+', '-', name)[0]

def create_ec2_instances(client, image_id, count, instance_type, security_groups, user_data, bdm, iam_role):
    reservations = client.create_instances(
        ImageId=image_id,
        MinCount=count,
        MaxCount=count,
        InstanceType=instance_type,
        SecurityGroups=security_groups,
        UserData=user_data,
        BlockDeviceMappings=bdm,
        InstanceInitiatedShutdownBehavior='terminate',
        IamInstanceProfile={
            "Name": iam_role,
        }
    )
    return reservations

def tag_ec2_instance(instance, name, branch, commit, username, elasticsearch):
    tags=[
        {'Key': 'Name', 'Value': name},
        {'Key': 'branch', 'Value': branch},
        {'Key': 'commit', 'Value': commit},
        {'Key': 'started_by', 'Value': username},
    ]
    if elasticsearch == 'yes':
        tags.append({'Key': 'elasticsearch', 'Value': elasticsearch})
    instance.create_tags(Tags=tags)
    return instance


def run(wale_s3_prefix, image_id, instance_type, elasticsearch, cluster_size, cluster_name,
        branch=None, name=None, role='demo', profile_name=None, teardown_cluster=None):
    
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


    if not elasticsearch == 'yes':
        if cluster_name:
            config_file = ':cloud-config-cluster.yml'
        else:
            config_file = ':cloud-config.yml'
        user_data = subprocess.check_output(['git', 'show', commit + config_file]).decode('utf-8')
        data_insert = {
            'WALE_S3_PREFIX': wale_s3_prefix,
            'COMMIT': commit,
            'ROLE': role,
        }
        if cluster_name:
            data_insert['CLUSTER_NAME'] = cluster_name
        user_data = user_data % data_insert
        security_groups = ['ssh-http-https']
        iam_role = 'encoded-instance'
        count = 1
    else:
        if not cluster_name:
            print("Cluster must have a name")
            sys.exit(1)

        user_data = subprocess.check_output(['git', 'show', commit + ':cloud-config-elasticsearch.yml']).decode('utf-8')
        user_data = user_data % {
            'CLUSTER_NAME': cluster_name,
        }
        security_groups = ['elasticsearch-https']
        iam_role = 'elasticsearch-instance'
        count = int(cluster_size)

    instances = create_ec2_instances(ec2, image_id, count, instance_type, security_groups, user_data, BDM, iam_role)

    for i, instance in enumerate(instances):
        if elasticsearch == 'yes' and count > 1:
            print('Creating Elasticsearch cluster')
            tmp_name = "{}{}".format(name,i)
        else:
            tmp_name = name
        print('%s.%s.encodedcc.org' % (instance.id, domain))  # Instance:i-34edd56f
        instance.wait_until_exists()
        tag_ec2_instance(instance, tmp_name, branch, commit, username, elasticsearch)
        print('ssh %s.%s.encodedcc.org' % (tmp_name, domain))
        if domain == 'instance':
            print('https://%s.demo.encodedcc.org' % tmp_name)



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
        '--instance-type', default='c4.4xlarge',
        help="(defualts toc4.4xlarge for indexing) Switch to a smaller instance afterwards"
        "(m4.xlarge or c4.xlarge)")
    parser.add_argument('--profile-name', default=None, help="AWS creds profile")
    parser.add_argument('--elasticsearch', default=None, help="Launch an Elasticsearch instance")
    parser.add_argument('--cluster-size', default=2, help="Elasticsearch cluster size")
    parser.add_argument('--teardown-cluster', default=None, help="Takes down all the cluster launched from the branch")
    parser.add_argument('--cluster-name', default=None, help="Name of the cluster")
    args = parser.parse_args()

    return run(**vars(args))


if __name__ == '__main__':
    main()
