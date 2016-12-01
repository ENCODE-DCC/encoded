import boto3
import getpass
import re
import subprocess
import sys
import datetime
import base64
import json


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
class spot_client(object):
    def __init__(self):
        self._spotClient = None
    
    @property
    def spotClient(self):
        return self._spotClient

    @spotClient.setter
    def spotClient(self, value):
        self._spotClient = value

def get_spot_id(instance, client):
    SpotInstanceRequestId = instance['SpotInstanceRequests'][0]['SpotInstanceRequestId']
    #print(list(instance.values()))
    #print("SpotInstanceRequestId: %s" % SpotInstanceRequestId)
    return SpotInstanceRequestId

def get_spot_code(instance, client, spot_id):
    request = client.describe_spot_instance_requests(SpotInstanceRequestIds=[get_spot_id(instance, client)])
    #print(list(request.values()))
    code_status_start = request['SpotInstanceRequests'][0]['Status']
    code_status = code_status_start['Code']

    #print("\n Code Status: %s" % code_status)  
    #for key, value in request.items():
     #  if key == 'SpotInstanceRequests':
      #      for item in value:
       #         for i in item:
        #            if i == 'Status':
         #               for j in item[i]:
          #                  if j == 'Code':
           #                     code_status = item[i][j]
    return code_status

def wait_for_code_change(instance, client):
    spot_id = get_spot_id(instance, client)
    code_status = get_spot_code(instance, client, get_spot_id(instance, client ))

    if not get_spot_code(instance, client, spot_id) == 'fulfilled':
        print("waiting for spot request to be fulfilled")
        code_status = get_spot_code(instance, client, get_spot_id(instance, client))                     
        while code_status != 'fulfilled':
            if code_status == error_cleanup(code_status, instance, client):
                exit()
            waiting = client.describe_spot_instance_requests(SpotInstanceRequestIds=[get_spot_id(instance, client)])
            for key, value in waiting.items():
                if key == 'SpotInstanceRequests':
                    for item in value:
                        for i in item:
                            if i == 'Status':
                                for j in item[i]:
                                    if j == 'Code':
                                        code_status = item[i][j]
            if code_status == 'price-too-low':
                print("Spot Instance ERROR: Bid placed is too low.")
                cancel_spot(instance, client)
                exit()
        return code_status

def get_instance_id(instance, client):
    request = client.describe_spot_instance_requests(SpotInstanceRequestIds=[get_spot_id(instance, client)])
    instance_id = request['SpotInstanceRequests'][0]['InstanceId']
    #print("\n Instace ID: %s" % instance_id)
    return instance_id

def error_cleanup(code_status, instance, client):
    hold_ERROR_list = [
        'capacity-not-available',
        'capacity-oversubscribed',
        'not-scheduled-yet',
        'launch-group-constraint',
        'az-group-constraint',
        'placement-group-constraint',
        'constraint-not-fulfillable'
    ]

    if code_status in hold_ERROR_list:
        print('------------ERROR-------------')
        print('Spot Instance ERROR: %s' % code_status)
        cancel_spot(instance, client)
        exit()

def cancel_spot(instance, client):
    kill_spot = client.cancel_spot_instance_requests(SpotInstanceRequestIds=[get_spot_id(instance,client)])


def spot_instance_price_check(client, instance_type):
    highest = 0
    todaysDate = datetime.datetime.now()
    response = client.describe_spot_price_history(
        DryRun=False,
        StartTime=todaysDate,
        EndTime=todaysDate,
        InstanceTypes=[
            instance_type
        ],
        Filters=[
            {
                'Name': 'availability-zone',
                'Values': [
                    'us-west-2a',
                    'us-west-2b',
                    'us-west-2c'
                ],

                'Name': 'product-description',
                'Values': [
                    'Linux/UNIX (Amazon VPC)'
                ]
            },
        ]
    )
    # dragons teeth lie below

    for key, value in response.items():

        if key == 'SpotPriceHistory':
            for item in value:
                for i in item:
                    if i == 'SpotPrice':
                        print("SpotPrice: %s" % item[i])

                        if float(item[i]) > highest:
                            highest = float(item[i])
    print("Highest price: %f" % highest)

    return highest

def spot_instances(client, spot_price, count, image_id, instance_type, security_groups, user_data, iam_role, bdm):
    responce = client.request_spot_instances(
    DryRun=False,
    SpotPrice=spot_price,
    InstanceCount=1,
    Type='one-time',
    LaunchSpecification={
        'ImageId': image_id,
        'SecurityGroups': list(security_groups),
        'UserData': user_data,
        'InstanceType': instance_type,
        'Placement': {
            'AvailabilityZone': 'us-west-2c'
        },
        'BlockDeviceMappings': bdm,
        'IamInstanceProfile': {
            "Name": iam_role,
        }
        }
    )
    code_status = wait_for_code_change(responce, client)
    if not code_status == 'fufilled':
        code_status = wait_for_code_change(responce, client)
    return responce

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

def tag_ec2_instance(instance, name, branch, commit, username, elasticsearch, cluster_name):
    tags=[
        {'Key': 'Name', 'Value': name},
        {'Key': 'branch', 'Value': branch},
        {'Key': 'commit', 'Value': commit},
        {'Key': 'started_by', 'Value': username},
    ]
    if elasticsearch == 'yes':
        tags.append({'Key': 'elasticsearch', 'Value': elasticsearch})
    if cluster_name != None:
        tags.append({'Key': 'ec_cluster_name', 'Value': cluster_name})
    instance.create_tags(Tags=tags)
    return instance

def tag_spot_instance(instance, name, branch, commit, username, elasticsearch, client, cluster_name):
    tags=[
        {'Key': 'Name', 'Value': name},
        {'Key': 'branch', 'Value': branch},
        {'Key': 'commit', 'Value': commit},
        {'Key': 'started_by', 'Value': username},
    ]
    if elasticsearch == 'yes':
        tags.append({'Key': 'elasticsearch', 'Value': elasticsearch})
    if not cluster_name == None:
        tags.append({'Key': 'ec_cluster_name', 'Value': cluster_name})
    instance_id = client.create_tags(Resources=[get_instance_id(instance, client)], Tags=tags)
    return instance_id

def run(wale_s3_prefix, image_id, instance_type, elasticsearch, spot_instance, spot_price, cluster_size, cluster_name, check_price,
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
    
    if check_price:
        ec2_spot = boto3.client('ec2')
        get_spot_price = spot_instance_price_check(ec2_spot, instance_type)
        exit()

    if spot_instance:
        print("spot_instance check worked")
        ec2_spot = boto3.client('ec2')
        # issue with base64 encoding so no decoding in utc-8 and recoding in base64 then decoding in base 64.
        config_file = ':cloud-config.yml'
        user_config = subprocess.check_output(['git', 'show', commit + ':cloud-config.yml'])
        user_data_b64 = base64.b64encode(user_config)
        user_data = user_data_b64.decode()
        client = spot_client()
        client.spotClient = ec2_spot
        print("security_groups: %s" % security_groups)
        instances = spot_instances(ec2_spot, spot_price, count, image_id, instance_type, security_groups, user_data, iam_role, BDM)
    else:
        instances = create_ec2_instances(ec2, image_id, count, instance_type, security_groups, user_data, BDM, iam_role)

    for i, instance in enumerate(instances):
        if elasticsearch == 'yes' and count > 1:
            print('Creating Elasticsearch cluster')
            tmp_name = "{}{}".format(name,i)
        else:
            tmp_name = name

        if not spot_instance:
            print('%s.%s.encodedcc.org' % (instance.id, domain))  # Instance:i-34edd56f
            instance.wait_until_exists()
            tag_ec2_instance(instance, tmp_name, branch, commit, username, elasticsearch, cluster_name)
            print('ssh %s.%s.encodedcc.org' % (tmp_name, domain))
            if domain == 'instance':
                print('https://%s.demo.encodedcc.org' % tmp_name)

    if spot_instance:
        tag_spot_instance(instances, tmp_name, branch, commit, username, elasticsearch, client.spotClient, cluster_name)
        print("Spot instance request had been completed, please check to be sure it was fufilled")

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
    parser.add_argument('--spot-instance', action='store_true', help="Launch as spot instance")
    parser.add_argument('--spot-price', default='0.70', help="Set price or keep default price of 0.70")
    parser.add_argument('--check-price', action='store_true', help="Check price on spot instances")
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
