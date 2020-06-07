import os
import boto3
import yaml

def instance_ips():
    ec2client = boto3.client('ec2', region_name='us-west-2')
    response = ec2client.describe_instances(
        Filters=[
            {
                'Name': 'tag:branch',
                'Values': [os.getenv('ENCD_GIT_BRANCH')]
            },
            {
                'Name': 'tag:kibana',
                'Values': ['true']
            }

        ]
    )
    ips= []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            if instance.get("PrivateIpAddress"):
                ips.append(instance.get("PrivateIpAddress"))
    return ips

def monitoring_settings(ips):
    settings = {
        'xpack.monitoring.exporters': {
            'id1': {
                'type': 'http',
                'host': [f'{ip}:9201' for ip in ips]
            }
        }
    }
    return settings

def add_settings_to_conf(settings, conf_file):
    with open(conf_file, 'a') as yaml_file:
        yaml.dump(settings, yaml_file, default_flow_style=False)


def main():
    settings = monitoring_settings(instance_ips())
    add_settings_to_conf(settings, '/etc/elasticsearch/elasticsearch.yml')

if __name__ == '__main__':
    main()
