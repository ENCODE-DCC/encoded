"""
Create ami from deploy encoded base ami build, waits for ami to be available, then tags it.

Input(in this order)
    instance_id: AWS instane id
    name_tag: demo, es-elect-data0, es-elect-datamaster, es-wait, and frontend
    user_name: your name

# Build types
export user_name=you
export instance_id=i-asdfaasdfasdf

## Demo:
    $ python create-ami.py $instance_id $user_name demo

## Es Elect - has two amis
    $ python create-ami.py $instance_id $user_name es-elect-data0
    $ python create-ami.py $instance_id $user_name es-elect-datamaster

## Frontend for to go with es
    $ python create-ami.py $instance_id $user_name frontend
"""
import argparse
import boto3

from time import sleep
from datetime import datetime


def _create_ami(ec2_client, ami_name, instance_id):
    response = ec2_client.create_image(
        Description="{} testing".format(ami_name),
        InstanceId=instance_id,
        Name=ami_name,
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200 and 'ImageId' in response:
        return response['ImageId']
    return None


def _tag_ami(ec2_resource, ami_id, ami_name, created_by, deployment_type, instance_id, date_now):
    print('Tagged', ami_name, ami_id)
    image = ec2_resource.Image(ami_id)
    image.create_tags(
        Tags=[
            {'Key': 'Name', 'Value': ami_name},
            {'Key': 'created_by', 'Value': created_by},
            {'Key': 'deployment_type', 'Value': deployment_type},
            {'Key': 'instance_id', 'Value': instance_id},
            {'Key': 'deployment_timestamp', 'Value': date_now},
        ]
    )


def _find_similar_amis(ec2_client, ami_name):
    filters = [
        {
            'Name': 'name',
            'Values': [ami_name],
        },
    ]
    response = ec2_client.describe_images(Filters=filters)
    ami_objs = []
    if 'ResponseMetadata' in response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        for res_img in response.get('Images', []):
            ami_obj = {
                'ami_id': res_img['ImageId'],
                'ami_name': res_img['Name'],
                'creation_date': res_img['CreationDate'],
                'description': res_img['Description'],
                'state': res_img['State'],
            }
            if 'Tags' in res_img:
                for tag in res_img['Tags']:
                    ami_obj[tag['Key']] = tag['Value']
                ami_objs.append(ami_obj)
    return ami_objs


def _get_ami_status(ec2_client, ami_id):
    response = ec2_client.describe_images(ImageIds=[ami_id])
    if 'ResponseMetadata' in response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        if response.get('Images'):
            return response['Images'][0].get('State')
    return None


def main():
    """Entry point"""
    main_args = _parse_args()
    
    session = boto3.Session(region_name='us-west-2', profile_name=main_args.profile_name)
    ec2_resource = session.resource('ec2')
    ec2_client = session.client('ec2')

    fuzzy_ami_name = 'encdami-{}'.format(
        main_args.deployment_type,
    )
    date_now = str(datetime.now())
    date_str = date_now.split('.')[0].replace(' ', '_').replace(':', '')
    ami_name = '{}-{}'.format(
        fuzzy_ami_name,
        date_str,
    )
    similar_amis = []
    print('\nLooking for similar amis: ', fuzzy_ami_name + '*')
    similar_amis = _find_similar_amis(ec2_client, fuzzy_ami_name + '*')
    instance_id_found = False
    for i, ami_obj in enumerate(similar_amis, 1):
        if ami_obj['instance_id'] == main_args.instance_id:
            instance_id_found = True
            print(
                '!!', i, ami_obj['ami_name'], 
                'instance_id=' + ami_obj['instance_id'], 
                'ami_id=' + ami_obj['ami_id'],
                ami_obj['state']
            )
        else:
            print(i, ami_obj['ami_name'], ami_obj['instance_id'], ami_obj['state'])
    if instance_id_found:
        print('\n ^^Ami for instance id already exists')
        return
    print('\nCreating ', ami_name, ' with instance ', main_args.instance_id)
    ami_id = _create_ami(ec2_client, ami_name, main_args.instance_id)
    sleep(10.0)
    if ami_id:
        print('\tWaiting for ami to be available')
        tick_max = 30
        ticks = 0
        while True:
            state = _get_ami_status(ec2_client, ami_id)
            if state == 'available':
                msg = "\t\t{}\t{}\t{}".format(ticks, ami_id, state)
                print(msg)
                _tag_ami(
                    ec2_resource,
                    ami_id,
                    ami_name,
                    main_args.created_by,
                    main_args.deployment_type,
                    main_args.instance_id,
                    date_now,
                )
                break
            sleep(1.0)
            if ticks == 0 or ticks >= tick_max:
                msg = "\t\t{}\t{}\t{}".format(ticks, ami_id, state)
                print(msg)
                ticks = 0
            ticks += 1
        key_name = main_args.deployment_type
        if main_args.profile_name == 'production':
            key_name += '-prod'
        print('\nAdd below to ami map in deploy script')
        print("# {} build on {}: {}".format(fuzzy_ami_name, date_now, ami_name))
        print("'{}': '{}',".format(key_name, ami_id))

def _parse_args():
    # pylint: disable=too-many-branches, too-many-statements
    parser = argparse.ArgumentParser(description="Create encoded ami")
    parser.add_argument('created_by', help='Your name')
    parser.add_argument('deployment_type', help='deployment type')
    parser.add_argument('instance_id', help='instance id')
    parser.add_argument('--profile-name', default='default', help="AWS creds profile")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()
