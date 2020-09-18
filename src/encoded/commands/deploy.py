"""
Encoded Application AWS Deployment Helper
"""
import io
import re

from argparse import ArgumentTypeError, ArgumentParser
from configparser import SafeConfigParser
from datetime import datetime
from getpass import getuser
from os.path import expanduser
from pathlib import Path
from subprocess import check_output
from sys import exit

from boto3 import Session


REPO_DIR = f"{str(Path().parent.absolute())}"


def _get_bdm(volume_size):
    allowed_values = [120, 200, 500]
    if int(volume_size) not in allowed_values:
        print(f"Volume size must be {allowed_values}")
        return None
    return [
        {
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'VolumeSize': int(volume_size),
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


def _load_configuration(conf_path):
    # Load config
    config_parser = SafeConfigParser()
    config_parser.read(conf_path)
    # Convert to dict
    conf_dict = {}
    for section in config_parser.sections():
        conf_dict[section] = {
            key: val
            for key, val in config_parser.items(section)
        }
    return conf_dict


def _nameify(in_str):
    name = ''.join(
        c if c.isalnum() else '-'
        for c in in_str.lower()
    ).strip('-')
    return re.subn(r'\-+', '-', name)[0]


def _read_ssh_key(identity_file):
    ssh_keygen_args = ['ssh-keygen', '-l', '-f', identity_file]
    finger_id = check_output(
        ssh_keygen_args
    ).decode('utf-8').strip()
    if finger_id:
        with open(identity_file, 'r') as key_file:
            ssh_pub_key = key_file.readline().strip()
            return ssh_pub_key
    return None


def _short_name(long_name):
    """
    Returns a short name for the branch name if found
    """
    if not long_name:
        return None
    regexes = [
        '(?:encd|sno)-[0-9]+',  # Demos
        '^v[0-9]+rc[0-9]+',     # RCs
        '^v[0-9]+x[0-9]+',      # Prod, Test
    ]
    result = long_name
    for regex_str in regexes:
        res = re.findall(regex_str, long_name, re.IGNORECASE)
        if res:
            result = res[0]
            break
    return result[:9].lower()


def _is_git_tag(branch, commit):
    tag_output = check_output(['git', 'tag', '--contains', commit]).strip().decode()
    for tag in tag_output.split('\n'):
        if tag == branch:
            return True
    git_cmd = ['git', 'branch', '-r', '--contains', commit]
    branch_output = check_output(git_cmd).decode()
    for branch_part in branch_output.split('\n'):
        branch_name = branch_part.strip().replace('origin/', '')
        if branch_name == branch:
            return False
    return None


def _read_file_as_utf8(config_file):
    with io.open(config_file, 'r', encoding='utf8') as file_handler:
        return file_handler.read()


def main():
    main_args = _parse_args()
    
    # Load config inis
    demo_ini = _load_configuration(f"{REPO_DIR}/demo-config.ini")
    dev_ini = _load_configuration(f"{REPO_DIR}/.dev-config.ini")
    for key, val in dev_ini.get('deployment', {}).items():
        demo_ini[key] = val
    for section, sec_dict in dev_ini.items():
        for key, val in sec_dict.items():
            demo_ini[section][key] = val
    
    # User name
    if not demo_ini['deployment']['username']:
        demo_ini['deployment']['username'] = getuser()
    # Branch
    if main_args.branch:
        branch = main.args.branch 
    elif demo_ini['deployment']['branch']:
        branch = demo_ini['deployment']['branch']
    else:
        branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
    
    # Commit
    commit = check_output(['git', 'rev-parse', '--short', branch]).decode('utf-8').strip()
    
    # Remote: origin or tags
    is_tag = _is_git_tag(branch, commit)
    if is_tag is None:
        print("Commit %r not in origin. Did you git push?" % commit)
        exit(1)
    remote = 'tags' if is_tag else 'origin'
    
    # Ssh Key
    ssh_key_path = expanduser(demo_ini['deployment']['identitiy_file'])
    ssh_key = _read_ssh_key(ssh_key_path)
    if not ssh_key:
        print('WARNING: Could not locate local ssh public key')

    # System Args
    system_args = demo_ini['system']
    system_args['git_branch'] = branch
    system_args['git_commit'] = commit
    system_args['git_remote'] = remote
    system_args['ssh_key'] = ssh_key

    system_args['cnf_git_branch'] = branch
    system_args['cnf_git_commit'] = commit
    system_args['cnf_git_remote'] = remote
    system_args['cnf_git_repo'] = system_args['git_repo']
    system_args['cnf_git_repo_dest'] = system_args['git_repo_dest']

    # Create user_data from template
    template_path = "{}/{}.yml".format(demo_ini['deployment']['conf_dir'], 'demo')
    demo_template = None
    with io.open(template_path, 'r', encoding='utf8') as file_handler:
        demo_template = file_handler.read()
    if not demo_template:
        print('Failure: Could not load yaml template')
        exit(1)
    user_data = demo_template % {
        key: val
        for key, val in system_args.items()
    }

    # Instance Args 
    aws_instance = demo_ini['aws_instance']
    aws_instance['bdm'] = _get_bdm(aws_instance['instance_volume_size'])
    if not aws_instance['bdm']:
        print('Could not create instance BDM?')
        exit(1)
    aws_instance['instance_name'] = _nameify(f"{_short_name(branch)}-{commit}-{demo_ini['deployment']['username']}")
    aws_instance['user_data'] = user_data
    if main_args.name:
        aws_instance['instance_name'] = main_args.name


    # Create Instance, Tag, wait for running, and console log
    ec2 = Session(
        region_name=aws_instance['region_name'],
        profile_name=aws_instance['profile_name'],
    ).resource('ec2')
    if any(ec2.instances.filter(
        Filters=[
            {'Name': 'tag:Name', 'Values': [aws_instance['instance_name']]},
            {'Name': 'instance-state-name',
             'Values': ['pending', 'running', 'stopping', 'stopped']},
        ])):
        print('An instance already exists with name: %s' % aws_instance['instance_name'])
        exit(1)
    # Create 
    instances = ec2.create_instances(
        BlockDeviceMappings=aws_instance['bdm'],
        IamInstanceProfile={"Name": aws_instance['iam_role']},
        ImageId=aws_instance['image_id'],
        MinCount=int(aws_instance['instance_count']),
        MaxCount=int(aws_instance['instance_count']),
        InstanceType=aws_instance['instance_type'],
        InstanceInitiatedShutdownBehavior='terminate',
        KeyName=aws_instance['key_pair_name'],
        Placement={'AvailabilityZone': aws_instance['region_availability']},
        SecurityGroups=[aws_instance['security_group']],
        UserData=aws_instance['user_data'],
    )
    if not instances:
        print('Could not create instance?')
        exit(1)
    # Tag
    tags = [
        {'Key': key, 'Value': val}
        for key, val in {
                'lcl_deploy_datetime': str(datetime.today()),
                'utc_deploy_datetime': str(datetime.utcnow()),
                'account': 'cherry-lab',
                'arch': 'x86_64',
                'auto_resize': 'c5.4xlarge',
                'auto_shutdown': 'true',
                'detailA': 'notused',
                'detailB': 'notused',
                'detailC': 'notused',
                'ec_cluster_name': 'single',
                'elasticsearch': 'no',
                'elasticsearch_head': 'no',
                'git_branch': system_args['git_branch'],
                'git_commit': system_args['git_commit'],
                'git_repo': system_args['git_repo'],
                'git_remote': system_args['git_remote'],
                'Name': aws_instance['instance_name'],
                'project': 'encoded',
                'Role': 'encd-demo',
                'section': 'app-dev',
                'started_by': demo_ini['deployment']['username'],
            }.items()
    ]
    instances[0].create_tags(Tags=tags)
    # Wait
    instances[0].wait_until_running()
    # Console log
    instances[0].load()
    print('Deploying Demo')
    print(f"https://{aws_instance['instance_name']}.demo.encodedcc.org")
    print(f"ssh ubuntu@{instances[0].id}.instance.encodedcc.org")
    print(f"ssh ubuntu@{instances[0].public_dns_name} 'tail -f /var/log/cloud-init-output.log'")


def _parse_args():
    # pylint: disable=too-many-branches, too-many-statements

    def hostname(value):
        if value != _nameify(value):
            raise ArgumentTypeError(
                "%r is an invalid hostname, only [a-z0-9] and hyphen allowed." % value)
        return value

    parser = ArgumentParser(description="Deploy ENCODE on AWS")
    parser.add_argument('-b', '--branch', default=None, help="Git branch or tag")
    parser.add_argument('-n', '--name', default=None, type=hostname, help="Instance name")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
