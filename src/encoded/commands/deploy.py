"""
Encoded Application AWS Deployment Helper

- SpotClient was removed in EPIC-ENCD-4716/ENCD-4688-remove-unused-code-from-deploy.
"""
import argparse
import datetime
import getpass
import io
import re
import subprocess
import sys
import time

from base64 import b64encode
from difflib import Differ
from os.path import expanduser

import boto3


def nameify(in_str):
    name = ''.join(
        c if c.isalnum() else '-'
        for c in in_str.lower()
    ).strip('-')
    return re.subn(r'\-+', '-', name)[0]


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


def tag_ec2_instance(instance, tag_data, elasticsearch, cluster_name):
    tags = [
        {'Key': 'Name', 'Value': tag_data['name']},
        {'Key': 'branch', 'Value': tag_data['branch']},
        {'Key': 'commit', 'Value': tag_data['commit']},
        {'Key': 'started_by', 'Value': tag_data['username']},
    ]
    if elasticsearch == 'yes':
        tags.append({'Key': 'elasticsearch', 'Value': elasticsearch})
        # This if for integration with nagios server.
        # Only used on production.
        tags.append({'Key': 'Role', 'Value': 'data'})
    if cluster_name is not None:
        tags.append({'Key': 'ec_cluster_name', 'Value': cluster_name})
    instance.create_tags(Tags=tags)
    return instance


def _read_file_as_utf8(config_file):
    with io.open(config_file, 'r', encoding='utf8') as file_handler:
        return file_handler.read()


def read_ssh_key(identity_file):
    ssh_keygen_args = ['ssh-keygen', '-l', '-f', identity_file]
    fingerprint = subprocess.check_output(
        ssh_keygen_args
    ).decode('utf-8').strip()
    if fingerprint:
        with open(identity_file, 'r') as key_file:
            ssh_pub_key = key_file.readline().strip()
            return ssh_pub_key
    return None


def _get_bdm(main_args):
    return [
        {
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'VolumeSize': int(main_args.volume_size),
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


def get_user_data(commit, config_yaml, data_insert, main_args):
    ssh_pub_key = read_ssh_key(main_args.identity_file)
    if not ssh_pub_key:
        print(
            "WARNING: User is not authorized with ssh access to "
            "new instance because they have no ssh key"
        )
    data_insert['LOCAL_SSH_KEY'] = ssh_pub_key
    # aws s3 authorized_keys folder
    auth_base = 's3://encoded-conf-prod/ssh-keys'
    auth_type = 'prod'
    if main_args.profile_name != 'production':
        auth_type = 'demo'
    auth_keys_dir = '{auth_base}/{auth_type}-authorized_keys'.format(
        auth_base=auth_base,
        auth_type=auth_type,
    )
    data_insert['S3_AUTH_KEYS'] = auth_keys_dir
    data_insert['REDIS_PORT'] = main_args.redis_port
    user_data = config_yaml % data_insert
    return user_data


def _get_commit_sha_for_branch(branch_name):
    return subprocess.check_output(
        ['git', 'rev-parse', '--short', branch_name]
    ).decode('utf-8').strip()


def _get_instances_tag_data(main_args):
    instances_tag_data = {
        'branch': main_args.branch,
        'commit': None,
        'short_name': _short_name(main_args.name),
        'name': main_args.name,
        'username': None,
    }
    instances_tag_data['commit'] = _get_commit_sha_for_branch(instances_tag_data['branch'])
    if not subprocess.check_output(
            ['git', 'branch', '-r', '--contains', instances_tag_data['commit']]
        ).strip():
        print("Commit %r not in origin. Did you git push?" % instances_tag_data['commit'])
        sys.exit(1)
    instances_tag_data['username'] = getpass.getuser()
    if instances_tag_data['name'] is None:
        instances_tag_data['short_name'] = _short_name(instances_tag_data['branch'])
        instances_tag_data['name'] = nameify(
            '%s-%s-%s' % (
                instances_tag_data['short_name'],
                instances_tag_data['commit'],
                instances_tag_data['username'],
            )
        )
        if main_args.elasticsearch == 'yes':
            instances_tag_data['name'] = 'elasticsearch-' + instances_tag_data['name']
    return instances_tag_data


def _get_ec2_client(main_args, instances_tag_data):
    session = boto3.Session(region_name='us-west-2', profile_name=main_args.profile_name)
    ec2 = session.resource('ec2')
    if any(ec2.instances.filter(
            Filters=[
                {'Name': 'tag:Name', 'Values': [instances_tag_data['name']]},
                {'Name': 'instance-state-name',
                 'Values': ['pending', 'running', 'stopping', 'stopped']},
            ])):
        print('An instance already exists with name: %s' % instances_tag_data['name'])
        return None
    return ec2


def _get_run_args(main_args, instances_tag_data, config_yaml):
    master_user_data = None
    cc_dir='/home/ubuntu/encoded/cloud-config/deploy-run-scripts'
    if not main_args.elasticsearch == 'yes':
        security_groups = ['ssh-http-https']
        iam_role = 'encoded-instance'
        count = 1
        data_insert = {
            'WALE_S3_PREFIX': main_args.wale_s3_prefix,
            'COMMIT': instances_tag_data['commit'],
            'ROLE': main_args.role,
            'REGION_INDEX': 'False',
            'ES_IP': main_args.es_ip,
            'ES_PORT': main_args.es_port,
            'GIT_REPO': main_args.git_repo,
            'GIT_BRANCH': main_args.branch,
            'REDIS_IP': main_args.redis_ip,
            'REDIS_PORT': main_args.redis_port,
            'BATCHUPGRADE_VARS': ' '.join(main_args.batchupgrade_vars),
            'CC_DIR': cc_dir,
        }
        if main_args.cluster_name:
            data_insert['CLUSTER_NAME'] = main_args.cluster_name
            data_insert['REGION_INDEX'] = 'True'
        if main_args.set_region_index_to:
            data_insert['REGION_INDEX'] = main_args.set_region_index_to
        user_data = get_user_data(instances_tag_data['commit'], config_yaml, data_insert, main_args)
    else:
        if not main_args.cluster_name:
            print("Cluster must have a name")
            sys.exit(1)
        count = int(main_args.cluster_size)
        security_groups = ['elasticsearch-https']
        iam_role = 'elasticsearch-instance'
        data_insert = {
            'CLUSTER_NAME': main_args.cluster_name,
            'ES_DATA': 'true',
            'ES_MASTER': 'true',
            'MIN_MASTER_NODES': int(count/2 + 1),
            'GIT_REPO': main_args.git_repo,
            'GIT_BRANCH': main_args.branch,
            'CC_DIR': cc_dir,
        }
        if main_args.single_data_master:
            data_insert['ES_MASTER'] = 'false'
            data_insert['MIN_MASTER_NODES'] = 1
        user_data = get_user_data(instances_tag_data['commit'], config_yaml, data_insert, main_args)
        if main_args.single_data_master:
            master_data_insert = {
                'CLUSTER_NAME': main_args.cluster_name,
                'ES_DATA': 'false',
                'ES_MASTER': 'true',
                'MIN_MASTER_NODES': 1,
                'GIT_REPO': main_args.git_repo,
                'GIT_BRANCH': main_args.branch,
                'BATCHUPGRADE_VARS': ' '.join(main_args.batchupgrade_vars),
                'CC_DIR': cc_dir,
            }
            master_user_data = get_user_data(
                instances_tag_data['commit'],
                config_yaml,
                master_data_insert,
                main_args,
            )
    run_args = {
        'count': count,
        'iam_role': iam_role,
        'user_data': user_data,
        'security_groups': security_groups,
    }
    if master_user_data:
        run_args['master_user_data'] = master_user_data
    return run_args


def _get_instance_output(
        instances_tag_data,
        attach_dm=False,
        given_name=None,
        is_production=False,
):
    hostname = '{}.{}.encodedcc.org'.format(
        instances_tag_data['id'],
        instances_tag_data['domain'],
    )
    name_to_use = given_name if given_name else instances_tag_data['short_name']
    suffix = '-dm' if attach_dm else ''
    domain = 'demo'
    if instances_tag_data['domain'] == 'production':
        domain = 'production'
    return [
        'Host %s%s.*' % (name_to_use, suffix),
        '  Hostname %s' % hostname,
        '  # https://%s.%s.encodedcc.org' % (instances_tag_data['name'], domain),
        '  # ssh ubuntu@%s' % hostname,
    ]


def _wait_and_tag_instances(main_args, run_args, instances_tag_data, instances, cluster_master=False):
    tmp_name = instances_tag_data['name']
    instances_tag_data['domain'] = 'production' if main_args.profile_name == 'production' else 'instance'
    output_list = ['']
    is_elasticsearch = main_args.elasticsearch == 'yes'
    is_cluster_master = False
    is_cluster = False
    if is_elasticsearch and run_args['count'] > 1:
        if cluster_master and run_args['master_user_data']:
            is_cluster_master = True
            output_list.append('Creating Elasticsearch Master Node for cluster')
        else:
            is_cluster = True
            output_list.append('Creating Elasticsearch cluster')
    created_cluster_master = False
    for i, instance in enumerate(instances):
        instances_tag_data['name'] = tmp_name
        instances_tag_data['id'] = instance.id
        if is_cluster_master:
            # Hack: current tmp_name was the last data cluster, so remove '4'
            instances_tag_data['name'] = "{}{}".format(tmp_name[0:-1], 'master')
        elif is_cluster:
            instances_tag_data['name'] = "{}{}".format(tmp_name, i)
        if is_cluster_master or (is_cluster and not created_cluster_master):
            created_cluster_master = True
            output_list.extend(_get_instance_output(
                instances_tag_data,
                attach_dm=True,
                given_name=main_args.name,
            ))
        if is_cluster:
            output_list.append('  # Data Node %d: %s' % (i, instance.id))
        elif not is_cluster:
            output_list.extend(
                _get_instance_output(
                    instances_tag_data,
                    given_name=main_args.name,
                )
            )
        instance.wait_until_exists()
        tag_ec2_instance(instance, instances_tag_data, main_args.elasticsearch, main_args.cluster_name)
    for output in output_list:
        print(output)


def _get_cloud_config_yaml(
        branch=None,
        conf_dir=None,
        cluster_name=None,
        elasticsearch=None,
        no_es=False,
        build_new_config=False,
        use_local_config=False,
        single_data_master=False,
    ):
    build_dir = "{}/prebuilt-config-yamls".format(conf_dir)
    build_files_dir = None
    if build_new_config:
        build_dir = "{}/{}".format(
            conf_dir,
            'config-build-files',
        )
        build_files_dir = "{}/{}".format(
            build_dir,
            'cc-parts',
        )
    filename = 'demo.yml'
    if single_data_master:
        if elasticsearch == 'yes':
            filename = 'es-wait-head.yml'
        else:
            filename = 'es-head.yml'
    elif no_es:
        filename = 'frontend.yml'
    elif elasticsearch == 'yes':
        filename = 'es-elect-head.yml'
    filepath = build_dir + '/' + filename
    if build_new_config:
        pre_config_template = _read_file_as_utf8(filepath)
        replace_vars = set(re.findall('\%\((.*)\)s', pre_config_template))
        var_data_insert = {}
        for replace_var in replace_vars:
            var_data_path = "{}/{}.yml".format(
                build_files_dir,
                replace_var,
            )
            var_data = _read_file_as_utf8(var_data_path).strip()
            var_data_insert[replace_var] = var_data
        return pre_config_template % var_data_insert, filepath
    else:
        if use_local_config:
            return _read_file_as_utf8(filepath), filepath
        else:
            commit = _get_commit_sha_for_branch(branch)
            cmd_list = ['git', 'show', commit + ':' + filepath]
            return subprocess.check_output(cmd_list).decode('utf-8'), filepath
    return None, filepath


def _diff_configs(config_one, config_two):
    results = list(
        Differ().compare(
            config_one.splitlines(keepends=True),
            config_two.splitlines(keepends=True),
        )
    )
    is_clean = True
    for index, result in enumerate(results, 1):
        if not result[0] == ' ':
            print(index, result)
            is_clean = False
            break
    return is_clean


def _test_config(title, kwargs):
    print('\n')
    print(title)
    build_config, build_path = _get_cloud_config_yaml(**kwargs)
    kwargs['build_new_config'] = False
    prebuilt_config, prebuilt_path = _get_cloud_config_yaml(**kwargs)
    print('build cc path: {}'.format(build_path))
    print('build cc path: {}'.format(prebuilt_path))
    print('Diff: ')
    return _diff_configs(build_config, prebuilt_config)


def _test_cloud_configs(branch):
    import copy

    kwargs = {
        'branch': branch,
        'build_new_config': True,
        'cluster_name': 'dryruncc-cluster',
        'conf_dir': './cloud-config',
        'elasticsearch': None,
        'no_es': False,
        'single_data_master': False,
        'use_local_config': False,
    }

    # All systems on one machine, Current development demo
    # cloud-config.yml -> demo.yml
    title = 'Testing Demo with on board ES'
    demo_kwargs = copy.copy(kwargs)
    if not _test_config(title, demo_kwargs):
        return False

    title = 'Testing Prod/Test/RC/Clustered-Demo frontend with separate ES'
    frontend_kwargs = copy.copy(kwargs)
    frontend_kwargs.update({'no_es': True})
    frontend_kwargs.update({'cluster_name': 'dryruncc-cluster'})
    if not _test_config(title, frontend_kwargs):
        return False

    # ES data node cluster with one node elected as master
    # cloud-config-elasticsearch.yml -> es-elect-head.yml
    title = 'Testing ES cluster that self elects a head node'
    es_elect_head_kwargs = copy.copy(kwargs)
    es_elect_head_kwargs.update({
        'cluster_name': 'dryruncc-cluster',
        'elasticsearch': 'yes',
    })
    if not _test_config(title, es_elect_head_kwargs):
        return False

    # ES data node cluster that needs a es head node
    # cloud-config-elasticsearch.yml -> es-wait-head.yml
    title = 'Testing ES cluster that wait for a head node to be built'
    es_wait_head_kwargs = copy.copy(kwargs)
    es_wait_head_kwargs.update({
        'cluster_name': 'dryruncc-cluster',
        'elasticsearch': 'yes',
        'single_data_master': True,
    })
    if not _test_config(title, es_wait_head_kwargs):
        return False

    # ES head data node for data node cluster
    # cloud-config-elasticsearch.yml -> es-head.yml
    title = 'Testing ES cluster head node, required for wait es cluster'
    es_head_kwargs = copy.copy(kwargs)
    es_head_kwargs.update({
        'cluster_name': 'dryruncc-cluster',
        'single_data_master': True,
    })
    if not _test_config(title, es_head_kwargs):
        return False
    return True


def main():
    # Gather Info
    main_args = parse_args()
    # Test prebuilt and new build config yamls
    if main_args.dry_run_cc:
        if _test_cloud_configs(main_args.branch):
            sys.exit(0)
        sys.exit(5)
    # Normal Deployment
    config_yaml, _ = _get_cloud_config_yaml(
        main_args.branch,
        main_args.conf_dir,
        main_args.cluster_name,
        main_args.elasticsearch,
        main_args.no_es,
        build_new_config=main_args.build_new_config,
        use_local_config=main_args.use_local_config,
    )
    instances_tag_data = _get_instances_tag_data(main_args)
    if instances_tag_data is None:
        sys.exit(10)
    ec2_client = _get_ec2_client(main_args, instances_tag_data)
    if ec2_client is None:
        sys.exit(20)
    run_args = _get_run_args(main_args, instances_tag_data, config_yaml)
    if main_args.dry_run_aws:
        print('Dry Run AWS')
        print('main_args', main_args)
        print('run_args', run_args.keys())
        print('Dry Run AWS')
        sys.exit(30)
    bdm = _get_bdm(main_args)
    instances = ec2_client.create_instances(
        ImageId=main_args.image_id,
        MinCount=run_args['count'],
        MaxCount=run_args['count'],
        InstanceType=main_args.instance_type,
        SecurityGroups=run_args['security_groups'],
        UserData=run_args['user_data'],
        BlockDeviceMappings=bdm,
        InstanceInitiatedShutdownBehavior='terminate',
        IamInstanceProfile={
            "Name": run_args['iam_role'],
        },
        Placement={
            'AvailabilityZone': main_args.availability_zone,
        },
    )
    _wait_and_tag_instances(main_args, run_args, instances_tag_data, instances)
    if 'master_user_data' in run_args and main_args.single_data_master:
        # ES MASTER instance when deploying elasticsearch data clusters
        if run_args['master_user_data'] and run_args['count'] > 1 and main_args.elasticsearch == 'yes':
            instances = ec2_client.create_instances(
                ImageId='ami-2133bc59',
                MinCount=1,
                MaxCount=1,
                InstanceType='c5.9xlarge',
                SecurityGroups=['ssh-http-https'],
                UserData=run_args['master_user_data'],
                BlockDeviceMappings=bdm,
                InstanceInitiatedShutdownBehavior='terminate',
                IamInstanceProfile={
                    "Name": 'encoded-instance',
                },
                Placement={
                    'AvailabilityZone': main_args.availability_zone,
                },
            )
            _wait_and_tag_instances(main_args, run_args, instances_tag_data, instances, cluster_master=True)


def parse_args():

    def check_region_index(value):
        lower_value = value.lower()
        allowed_values = [
            'true', 't',
            'false', 'f'
        ]
        if value.lower() not in allowed_values:
            raise argparse.ArgumentTypeError(
                "Noncase sensitive argument '%s' is not in [%s]." % (
                    str(value),
                    ', '.join(allowed_values),
                )
            )
        if lower_value[0] == 't':
            return 'True'
        return 'False'

    def check_volume_size(value):
        allowed_values = ['120', '200', '500']
        if not value.isdigit() or value not in allowed_values:
            raise argparse.ArgumentTypeError(
                "%s' is not in [%s]." % (
                    str(value),
                    ', '.join(allowed_values),
                )
            )
        return value

    def hostname(value):
        if value != nameify(value):
            raise argparse.ArgumentTypeError(
                "%r is an invalid hostname, only [a-z0-9] and hyphen allowed." % value)
        return value

    parser = argparse.ArgumentParser(
        description="Deploy ENCODE on AWS",
    )
    parser.add_argument(
        '-i',
        '--identity-file',
        default="{}/.ssh/id_rsa.pub".format(expanduser("~")),
        help="ssh identity file path"
    )
    parser.add_argument('-b', '--branch', default=None, help="Git branch or tag")
    parser.add_argument('--build-new-config', action='store_true', help="Build cloud config yaml.")
    parser.add_argument('-n', '--name', default=None, type=hostname, help="Instance name")
    parser.add_argument('--dry-run-aws', action='store_true', help="Abort before ec2 requests.")
    parser.add_argument('--dry-run-cc', action='store_true', help="Abort after building cloud config.")
    parser.add_argument('--single-data-master', action='store_true',
            help="Create a single data master node.")
    parser.add_argument('--cluster-name', default=None, help="Name of the cluster")
    parser.add_argument('--cluster-size', default=2, help="Elasticsearch cluster size")
    parser.add_argument('--conf-dir', default='./cloud-config', help="Location of cloud build config")
    parser.add_argument('--elasticsearch', default=None, help="Launch an Elasticsearch instance")
    parser.add_argument('--es-ip', default='localhost', help="ES Master ip address")
    parser.add_argument('--es-port', default='9201', help="ES Master ip port")
    parser.add_argument('--image-id', default='ami-2133bc59',
                        help=(
                            "https://us-west-2.console.aws.amazon.com/ec2/home"
                            "?region=us-west-2#LaunchInstanceWizard:ami=ami-2133bc59"
                        ))
    parser.add_argument('--instance-type', default='c5.9xlarge',
                        help="c5.9xlarge for indexing. Switch to a smaller instance (m5.xlarge or c5.xlarge).")
    parser.add_argument('--profile-name', default=None, help="AWS creds profile")
    parser.add_argument('--no-es', action='store_true', help="Use non ES cloud condfig")
    parser.add_argument('--redis-ip', default='localhost', help="Redis IP.")
    parser.add_argument('--redis-port', default=6379, help="Redis Port.")
    parser.add_argument('--set-region-index-to', type=check_region_index,
                        help="Override region index in yaml to 'True' or 'False'")
    parser.add_argument('--use-local-config', action='store_true', help="Use local config file in current directory")
    parser.add_argument('--volume-size', default=200, type=check_volume_size,
                        help="Size of disk. Allowed values 120, 200, and 500")
    parser.add_argument('--wale-s3-prefix', default='s3://encoded-backups-prod/production')
    parser.add_argument('--candidate', action='store_true', help="Deploy candidate instance")
    parser.add_argument('--release-candidate', action='store_true', help="Deploy release-candidate instance")
    parser.add_argument(
        '--test', action='store_const', default='demo', const='test', dest='role',
        help="Deploy to production AWS")
    parser.add_argument('--availability-zone', default='us-west-2a',
        help="Set EC2 availabilty zone")
    parser.add_argument('--git-repo', default='https://github.com/ENCODE-DCC/encoded.git',
            help="Git repo to checkout branches: https://github.com/{user|org}/{repo}.git")
    parser.add_argument('--batchupgrade-vars', nargs=4, default=['1000', '1', '16', '1'],
        help=(
            "Set batchupgrade vars for demo only "
            "Ex) --batchupgrade-vars 1000 1 8 1 "
            "Where the args are batchsize, chunksize, processes, and maxtasksperchild"
        )
    )
    # Set Role
    # - 'demo' role is default for making single or clustered
    # applications for feature building
    # - '--test' will set role to test
    # - 'rc' role is for Release-Candidate QA testing and
    # is the same as 'demo' except batchupgrade will be skipped during deployment.
    # This better mimics production but require a command be run after deployment.
    # - 'candidate' role is for production release that potential can
    # connect to produciton data.
    args = parser.parse_args()
    if not args.role == 'test':
        if args.release_candidate:
            args.role = 'rc'
            args.candidate = False
        elif args.candidate:
            args.role = 'candidate'
    # Add branch arg
    if not args.branch:
        args.branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        ).decode('utf-8').strip()
    return args


if __name__ == '__main__':
    main()
