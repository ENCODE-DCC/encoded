"""
Encoded Application AWS Deployment Helper
"""
import argparse
import getpass
import io
import re
import subprocess
import sys
import copy
from time import sleep

from difflib import Differ
from os.path import expanduser
from datetime import datetime

import boto3
from pathlib import Path


REPO_DIR = f"{str(Path().parent.absolute())}"


def _load_configuration(conf_path):
    # Load config
    from configparser import SafeConfigParser
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



# AWS/EC2 - Deploy Cloud Config
def _tag_ec2_instance(
        instance,
        tag_data,
        elasticsearch,
        cluster_name,
        image_id,
        role='demo',
        profile_name='default',
        dry_run=False,
        arm_arch=False,
        cluster_master=False,
    ):
    # Defaults to demo development
    tags_dict = {
        # Org
        'project': 'encoded',
        'section': 'app',
        'account': 'cherry-lab',
        'started_by': tag_data['username'],
        # Instance
        'Name': tag_data['name'],
        'arch': 'x86_64',
        'branch': tag_data['branch'],
        'commit': tag_data['commit'],
        'elasticsearch': 'no',
        'elasticsearch_head': 'no',
        'ec_cluster_name': cluster_name if cluster_name else 'single',
        'lcl_deploy_datetime': str(datetime.today()),
        'utc_deploy_datetime': str(datetime.utcnow()),
        # Devops
        'auto_shutdown': 'true',
        'auto_resize': 'c5.4xlarge',
        'elastic_ip_swtich_datatime': 'na',
        'Role': 'encd',
        # User: User editable tags for personal use.
        'detailA': 'notused',
        'detailB': 'notused',
        'detailC': 'notused',
    }
    if profile_name == 'default': 
        if role == 'rc':
            tags_dict['Role'] += '-new-rc'
            tags_dict['section'] += '-rc'
            tags_dict['ec_cluster_name'] = cluster_name
            tags_dict['auto_shutdown'] = 'false'
            tags_dict['auto_resize'] = 'na'
        elif role == 'test':
            tags_dict['Role'] += '-new-test'
            tags_dict['section'] += '-test'
            tags_dict['ec_cluster_name'] = cluster_name
            tags_dict['auto_shutdown'] = 'false'
            tags_dict['auto_resize'] = 'na'
            tags_dict['elastic_ip_swtich_datatime'] = 'pending'
        else:
            if tag_data['is_qa_demo']:
                tags_dict['Role'] += '-qa'
                tags_dict['section'] += '-qa'
            else:
                tags_dict['Role'] += '-dev'
                tags_dict['section'] += '-dev'
            if cluster_name:
                tags_dict['Role'] += '-cluster'
                tags_dict['section'] += '-cluster'
    elif profile_name == 'production':
        tags_dict['account'] = 'encode-prod'
        if role == 'candidate':
            tags_dict['Role'] += '-new-prod'
            tags_dict['section'] += '-prod'
            tags_dict['ec_cluster_name'] = cluster_name
            tags_dict['auto_shutdown'] = 'false'
            tags_dict['auto_resize'] = 'na'
            tags_dict['elastic_ip_swtich_datatime'] = 'pending'
    if elasticsearch:
        # the role tags for data machines are used for nagios monitoring
        tags_dict['Role'] += '-data'
        tags_dict['elasticsearch'] = 'yes'
        tags_dict['auto_resize'] = 'na'
        tags_dict['elastic_ip_swtich_datatime'] = 'na'
        if cluster_master:
            tags_dict['elasticsearch_head'] = 'yes'
            tags_dict['Role'] += 'head'
    if arm_arch:
        tags_dict['arch'] = 'arm'
    # Create tags list
    tags = []
    for key, val in tags_dict.items():
        tags.append({'Key': key, 'Value': val})
    if not dry_run and instance:
        instance.create_tags(Tags=tags)
    return tags, tags_dict


def _wait_and_tag_instances(
        main_args,
        run_args,
        instances_tag_data,
        instances,
        image_id,
        cluster_master=False
):
    tmp_name = instances_tag_data['name']
    instances_tag_data['domain'] = 'instance'
    if main_args.profile_name == 'production':
        instances_tag_data['domain'] = 'production'
    ssh_host_name = None
    is_cluster_master = False
    is_cluster = False
    if (main_args.es_wait or main_args.es_elect) and run_args['count'] >= 1:
        if cluster_master and run_args['master_user_data']:
            is_cluster_master = True
        else:
            is_cluster = True
    # Wait for one instance to start running + a little more
    instances[0].wait_until_running()
    sleep(30)
    instances_info = {}
    for i, instance in enumerate(instances):
        info_type = 'unknown'
        # Reload to get new data
        instance.load()
        instances_tag_data['name'] = tmp_name
        instances_tag_data['id'] = instance.id
        instances_tag_data['url'] = 'None'
        if is_cluster_master:
            info_type = 'cluster_master'
            instances_tag_data['name'] = "{}master".format(tmp_name[0:-1])
        elif is_cluster:
            info_type = 'cluster_node_{}'.format(i)
            instances_tag_data['name'] = "{}-data{}".format(tmp_name, i)
        if main_args.node_name:
            # override default node name
            # This is to add a node to a preexisting cluster since there is a name check
            instances_tag_data['name'] = main_args.node_name
        url = None 
        if not is_cluster and not cluster_master:
            # Demos and frontends
            # - build type
            if main_args.cluster_name:
                info_type = 'frontend'
            else:
                info_type = 'demo'
            # - url for prod and demo
            if instances_tag_data['domain'] == 'production':
                url = 'http://%s.%s.encodedcc.org' % (instances_tag_data['name'], 'production')
            else:
                url = 'https://%s.%s.encodedcc.org' % (instances_tag_data['name'], 'demo')
        if url:
            instances_tag_data['url'] = url
        # Set Tags
        _tag_ec2_instance(
            instance, instances_tag_data,
            (main_args.es_wait or main_args.es_elect),
            main_args.cluster_name,
            role=main_args.role,
            profile_name=main_args.profile_name,
            arm_arch=main_args.arm_image_id,
            image_id=image_id,
            cluster_master=cluster_master,
        )
        # Create return info
        instances_info[info_type] = {
            'instance_id_domain': "{}.{}.encodedcc.org".format(
                instance.id,
                instances_tag_data['domain'],
            ),
            'instance_id': instance.id,
            'public_dns': instance.public_dns_name,
            'private_ip': instance.private_ip_address,
            'name': instances_tag_data['name'],
            'url': url,
            'username': instances_tag_data['username'],
        }
    return instances_info


# Cloud Config
def _nameify(in_str):
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


def _read_file_as_utf8(config_file):
    with io.open(config_file, 'r', encoding='utf8') as file_handler:
        return file_handler.read()


def _write_str_to_file(filepath, str_data):
    with io.open(filepath, 'w') as file_handler:
        return file_handler.write(str_data)


def _read_ssh_key(identity_file):
    ssh_keygen_args = ['ssh-keygen', '-l', '-f', identity_file]
    finger_id = subprocess.check_output(
        ssh_keygen_args
    ).decode('utf-8').strip()
    if finger_id:
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
                'VolumeType': 'gp3',
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


def _get_user_data(config_yaml, data_insert, main_args):
    ssh_pub_key = _read_ssh_key(main_args.identity_file)
    if not ssh_pub_key:
        print(
            "WARNING: User is not authorized with ssh access to "
            "new instance because they have no ssh key"
        )
    data_insert['SSH_KEY'] = ssh_pub_key
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
    user_data = config_yaml % data_insert
    return user_data


def _get_commit_sha_for_branch(branch_name):
    return subprocess.check_output(
        ['git', 'rev-parse', '--short', branch_name]
    ).decode('utf-8').strip()


def _get_instances_tag_data(main_args, build_type_template_name):
    instances_tag_data = {
        'branch': main_args.branch,
        'commit': None,
        'short_name': _short_name(main_args.name),
        'name': main_args.name,
        'username': None,
        'build_type': build_type_template_name,
        'is_qa_demo': main_args.is_qa_demo,
    }
    subprocess.check_output(['git', 'fetch', '--tags'])
    instances_tag_data['commit'] = _get_commit_sha_for_branch(instances_tag_data['branch'])
    # check if commit is a tag first then branch
    is_tag = False
    tag_output = subprocess.check_output(
        ['git', 'tag', '--contains', instances_tag_data['commit']]
    ).strip().decode()
    for tag in tag_output.split('\n'):
        if tag == main_args.branch:
            is_tag = True
    is_branch = False
    if not is_tag:
        git_cmd = ['git', 'branch', '-r', '--contains', instances_tag_data['commit']]
        branch_output = subprocess.check_output(git_cmd).decode()
        for branch in branch_output.split('\n'):
            branch_name = branch.strip().replace('origin/', '')
            if branch_name == main_args.branch:
                is_branch = True
    if not is_tag and not is_branch:
        print("Commit %r not in origin. Did you git push?" % instances_tag_data['commit'])
    else:
        instances_tag_data['username'] = main_args.username if main_args.username else getpass.getuser()
        if instances_tag_data['name'] is None:
            instances_tag_data['short_name'] = _short_name(instances_tag_data['branch'])
            instances_tag_data['name'] = _nameify(
                '%s-%s-%s' % (
                    instances_tag_data['short_name'],
                    instances_tag_data['commit'],
                    instances_tag_data['username'],
                )
            )
            if main_args.es_wait or main_args.es_elect:
                instances_tag_data['name'] = 'elasticsearch-' + instances_tag_data['name']
    return instances_tag_data, is_tag, is_branch


def _get_ec2_client(main_args, instances_tag_data):
    session = boto3.Session(region_name='us-west-2', profile_name=main_args.profile_name)
    ec2 = session.resource('ec2')
    name_to_check = instances_tag_data['name']
    if main_args.node_name:
        if int(main_args.cluster_size) != 1:
            print('--node-name can only be used --cluster-size 1')
            return None
        name_to_check = main_args.node_name
    if any(ec2.instances.filter(
            Filters=[
                {'Name': 'tag:Name', 'Values': [name_to_check]},
                {'Name': 'instance-state-name',
                 'Values': ['pending', 'running', 'stopping', 'stopped']},
            ])):
        print('An instance already exists with name: %s' % name_to_check)
        return None
    return ec2


def _get_run_args(main_args, instances_tag_data, config_yaml, is_tag=False):
    build_type = instances_tag_data['build_type']  # template_name
    master_user_data = None
    git_remote = 'origin' if not is_tag else 'tags'
    home = "/srv/encoded"
    data_insert = {
        'APP_WORKERS': 'notused',
        'BATCHUPGRADE': 'true' if main_args.do_batchupgrade else 'false',
        'BATCHUPGRADE_VARS': 'notused',
        'BUILD_TYPE': build_type,
        'COMMIT': instances_tag_data['commit'],
        'CC_DIR': main_args.conf_dir_remote,
        'CLUSTER_NAME': 'NONE',
        'DEVELOP_SNOVAULT': 'true' if not main_args.no_develop_snovault else 'false',
        'ES_IP': main_args.es_ip,
        'ES_PORT': main_args.es_port,
        'ES_OPT_FILENAME': 'notused',
        'FE_IP': main_args.fe_ip,
        'FULL_BUILD': main_args.full_build,
        'GIT_BRANCH': main_args.branch,
        'GIT_REMOTE': git_remote,
        'GIT_REPO': main_args.git_repo,
        'HOME': home,
        'INDEX_PRIMARY': 'false',
        'INDEX_VIS': 'false',
        'INDEX_REGION': 'true' if main_args.region_indexer else 'false',
        'INDEX_PROCS': main_args.index_procs,
        'INDEX_CHUNK_SIZE': main_args.index_chunk_size,
        'INSTALL_TAG': 'encd-install',
        'JVM_GIGS': 'notused',
        'PG_VERSION': main_args.postgres_version,
        'PG_OPEN': 'true' if main_args.pg_open else 'false',
        'PG_IP': main_args.pg_ip,
        'PY3_PATH': '/usr/bin/python3.6',
        'REDIS_PORT': main_args.redis_port,
        'REMOTE_INDEXING': 'true' if main_args.remote_indexing else 'false',
        'ROLE': main_args.role,
        'S3_AUTH_KEYS': 'addedlater',
        'SCRIPTS_DIR': "{}/run-scripts".format(main_args.conf_dir_remote),
        "VENV_DIR": "{}/venv".format(home),
        'WALE_S3_PREFIX': main_args.wale_s3_prefix,
    }
    if build_type == 'es-nodes':
        count = int(main_args.cluster_size)
        security_groups = ['elasticsearch-https']
        iam_role = main_args.iam_role_es
        es_opt = 'es-cluster-wait.yml' if main_args.es_wait else 'es-cluster-elect.yml'
        data_insert.update({
            'CLUSTER_NAME': main_args.cluster_name,
            'ES_OPT_FILENAME': es_opt,
            'JVM_GIGS': main_args.jvm_gigs,
        })
        user_data = _get_user_data(config_yaml, data_insert, main_args)
        # Additional head node: FYI: --node-name is used for adding/recreating an es node in 
        #  an already existing cluster
        if main_args.es_wait and main_args.node_name is None:
            master_data_insert = copy.copy(data_insert)
            master_data_insert.update({
                'ES_OPT_FILENAME': 'es-cluster-head.yml',
            })
            master_user_data = _get_user_data(
                config_yaml,
                master_data_insert,
                main_args,
            )
    else:
        # Frontends(app-es-pg, app-es, app-pg, app)
        security_groups = ['ssh-http-https']
        iam_role = main_args.iam_role
        count = 1
        data_insert.update({
            'APP_WORKERS': main_args.app_workers,
            'BATCHUPGRADE_VARS': ' '.join(main_args.batchupgrade_vars),
            'ROLE': main_args.role,
        })
        if build_type == 'app':
            data_insert.update({
                'CLUSTER_NAME': main_args.cluster_name,
            })
            if main_args.no_indexing:
                data_insert.update({
                    'INDEX_PRIMARY': 'false',
                    'INDEX_VIS': 'false',
                    'INDEX_REGION': 'false',
                })
        elif build_type == 'app-pg':
            data_insert.update({
                'CLUSTER_NAME': main_args.cluster_name,
                'INDEX_PRIMARY': 'true',
                'INDEX_VIS': 'true',
            })
            if main_args.no_indexing:
                data_insert.update({
                    'INDEX_PRIMARY': 'false',
                    'INDEX_VIS': 'false',
                    'INDEX_REGION': 'false',
                })
        elif build_type == 'app-es':
            # This needs a remote datbase like in rds
            data_insert.update({
                'INDEX_PRIMARY': 'true',
                'INDEX_VIS': 'true',
            })
        else: 
            # 'app-es-pg' == "Demo"
            data_insert.update({
                'JVM_GIGS': main_args.jvm_gigs,
                'ES_OPT_FILENAME': 'es-demo.yml',
                'INDEX_PRIMARY': 'true',
                'INDEX_VIS': 'true',
            })
        if main_args.primary_indexing:
            data_insert.update({
                'INDEX_PRIMARY': 'true',
            })
        user_data = _get_user_data(config_yaml, data_insert, main_args)

    run_args = {
        'count': count,
        'iam_role': iam_role,
        'master_user_data': master_user_data,
        'user_data': user_data,
        'security_groups': security_groups,
        'key-pair-name': 'encoded-demos' if main_args.role != 'candidate' else 'encoded-prod',
    }
    if main_args.profile_name == 'production' and main_args.role != 'candidate':
        run_args['key-pair-name'] += '-prod'
    return run_args


def _get_cloud_config_yaml(main_args):
    """
    This will return a config yaml file built from a template and template parts
    - There will still be run variables in the template.
    """
    # pylint: disable=too-many-locals, too-many-return-statements
    
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

    def _get_prebuild_config_template():
        read_config_path = "{}/{}/{}.yml".format(
            main_args.conf_dir,
            'assembled-templates',
            main_args.use_prebuilt_config
        )
        return _read_file_as_utf8(read_config_path)

    def _build_config_template(template_name):
        template_path = "{}/{}-template.yml".format(main_args.conf_dir, template_name)
        built_config_template = _read_file_as_utf8(template_path)
        replace_vars = set(re.findall(r'\%\((.*)\)s', built_config_template))
        # Replace template part vars in template.  Run vars are in template-parts.
        template_parts_dir = "{}/{}".format(main_args.conf_dir, 'template-parts')
        template_parts_insert = {}
        for replace_var_filename in replace_vars:
            replace_var_path = "{}/{}.yml".format(
                template_parts_dir,
                replace_var_filename,
            )
            replace_var_data = _read_file_as_utf8(replace_var_path).strip()
            template_parts_insert[replace_var_filename] = replace_var_data
        return built_config_template % template_parts_insert

    # Incompatibile build arguments
    if main_args.postgres_version and main_args.postgres_version not in ['9.3', '11']:
        print("Error: postgres_version must be '9.3' or '11'")
        return None, None, None
    if (main_args.es_elect or main_args.es_wait) and not main_args.cluster_name:
        print('Error: --cluster-name required for --es-wait and --es-elect')
        return None, None, None
    if main_args.diff_configs and not main_args.use_prebuilt_config:
        print('Error: --diff-configs must have --use-prebuilt-config config to diff against')
        return None, None, None
    if not (main_args.es_elect or main_args.es_wait) and main_args.cluster_name and main_args.es_ip == 'localhost':
        print('Error: --cluster-name requires --es-ip')
        return None, None, None
    if main_args.cluster_name and main_args.es_ip == 'localhost' and not main_args.pg_ip == '':
        print('Error: --cluster-name cannot be used without --es-ip')
        return None, None, None
    # Determine template 
    template_name = 'app-es-pg'
    if main_args.es_elect or main_args.es_wait:
        template_name = 'es-nodes'
    elif main_args.cluster_name:
        if not main_args.es_ip == 'localhost' and main_args.pg_ip == '':
            # Standard cluster frontend with remote es and local pg
            template_name = 'app-pg'
        elif not main_args.es_ip == 'localhost' and not main_args.pg_ip == '':
            # Remote es and remote pg, just the application
            template_name = 'app'
        else:
            print('Error: Could not find template with --cluster-name')
            return None, None, None
    elif main_args.no_indexing:
        # Standard cluster frontend with remote es and local pg
        # but the apache build_conf will not add the indexing processes
        # See env vars with --dry-run 
            # 'INDEX_PRIMARY': 'false',
            # 'INDEX_VIS': 'false',
            # 'INDEX_REGION': 'false',
        template_name = 'app-pg'
    elif not main_args.pg_ip == '':
        # Local es and remote pg
        template_name = 'app-es'
    # Determine config build method
    if main_args.use_prebuilt_config and not main_args.diff_configs:
        # Read a prebuilt config file from local dir and use for deployment
        prebuilt_config_template = _get_prebuild_config_template()
        if prebuilt_config_template:
            return prebuilt_config_template, None, template_name
        return None, None, template_name
    # Build config from template using template-parts
    config_template = _build_config_template(template_name)
    if main_args.diff_configs:
        # Read a prebuilt config file from local dir and use for diff
        prebuilt_config_template = _get_prebuild_config_template()
        print('Diffing')
        _diff_configs(config_template, prebuilt_config_template)
        print('Diff Done')
        return config_template, None, template_name
    if main_args.save_config_name:
        # Having write_file_path set will not deploy
        # After creating a new config rerun
        #  with use_prebuilt_config=subpath/config_name
        config_name = "{}-{}".format(main_args.save_config_name, template_name)
        write_file_path = "{}/{}/{}.yml".format(
            main_args.conf_dir,
            'assembled-templates',
            config_name,
        )
        return config_template, write_file_path, template_name
    return config_template, None, template_name


def _write_config_to_file(build_config, build_path, template_name):
    print(f' Created assembeled template\n\t{build_path}')
    _write_str_to_file(build_path, build_config)
    # Create example deployment command
    deployment_args = []
    config_name = ''
    for index, arg in enumerate(sys.argv):
        if arg == '--save-config-name':
            config_name = sys.argv[index + 1]
            deployment_args.extend(sys.argv[index + 2:])
            break
        deployment_args.append(arg)
    deploy_cmd = ' '.join(deployment_args)
    if template_name in ['app-pg', 'app']:
        deploy_cmd += ' --es-ip $ES_HEAD_IP'
    if template_name in ['app-es', 'app']:
        deploy_cmd += ' --pg-ip $PG_DB_IP'
    deploy_cmd += f' --use-prebuilt-config {config_name}-{template_name}'
    print(f' Deploy with\n\t$ {deploy_cmd}')
    print(f' Diff with on the fly assembly\n\t$ {deploy_cmd} --diff-configs')
    # prebuild = "--use-prebuilt-config {}-{}".format(config_name, template_name)
    # print("    * Diff Build/Prebuild: ${} {} --diff-configs".format(deploy_cmd, prebuild))
    # print("    * Deploy     Prebuild: ${} {}".format(deploy_cmd, prebuild))
    # print("    * Deploy        Build: ${}".format(deploy_cmd))


def main():
    """Entry point for deployment"""
    main_args = _parse_args()
    # Load repo default config
    default_demo_ini = f"{REPO_DIR}/demo-config.ini"
    ini_dict= _load_configuration(default_demo_ini)
    # Load developer overrides
    override_dev_ini = f"{REPO_DIR}/.dev-config.ini"
    override_ini_dict = _load_configuration(override_dev_ini)
    for key, val in override_ini_dict.get('deployment', {}).items():
        if val:
            ini_dict['deployment'][key] = val
    # Main args overridden by deployment conf dict
    for key, val in ini_dict['deployment'].items():
        if hasattr(main_args, key):
            if val:
                setattr(main_args, key, val)
        else:
            setattr(main_args, key, val)

    assembled_template, save_path, template_name = _get_cloud_config_yaml(main_args)
    if main_args.diff_configs:
        sys.exit(0)
    if not assembled_template or not template_name:
        print('# Failure: Could not determine configuration type')
        sys.exit(1)
    if save_path:
        _write_config_to_file(assembled_template, save_path, template_name)
        sys.exit(0)
    # Deploy Frontend, Demo, es elect cluster, or es wait data nodes
    indexing = False if main_args.no_indexing or template_name == 'app' else True
    print(f'\nDeploying {template_name} with indexing={indexing}')
    print("$ {}".format(' '.join(sys.argv)))
    instances_tag_data, is_tag, is_branch = _get_instances_tag_data(main_args, template_name)
    if instances_tag_data is None:
        print('Failure: No instances_tag_data')
        sys.exit(1)
    if not is_tag and not is_branch:
        print('Failure: Not a tag or branch')
        sys.exit(1)
    run_args = _get_run_args(main_args, instances_tag_data, assembled_template, is_tag=is_tag)
    # run_args has the asseblmed_template filled with run variables in 'user_data' key
    bdm = _get_bdm(main_args)
    if main_args.dry_run:
        print(f'\nDry Run')
        print(f'run_args dict keys: {run_args.keys()}')
        print(f'\nRun Variables.  In /etc/environment on instance')
        for line in run_args['user_data'].split('\n'):
            line = line.strip()
            if line[:5] == 'ENCD_':
                print(line)
        print('\ninstances_tag_data', instances_tag_data)
        print('\nis_tag:', is_tag, ', is_branch:', is_branch)
        print('\nInstance Tags:')
        tags, tags_dict = _tag_ec2_instance(
            None, instances_tag_data,
            (main_args.es_wait or main_args.es_elect),
            main_args.cluster_name,
            role=main_args.role,
            profile_name=main_args.profile_name,
            dry_run=True,
            arm_arch=main_args.arm_image_id,
            image_id=main_args.image_id,
        )
        for key, val in tags_dict.items():
            print(f"{key:28}:'{val}'")
        print('Dry Run')
        sys.exit(0)
    # AWS - Below
    print('Create instance and wait for running state')
    ec2_client = _get_ec2_client(main_args, instances_tag_data)
    if ec2_client is None:
        sys.exit(20)
    # Create aws demo instance or frontend instance
    # OR instances for es_wait nodes, es_elect nodes depending on count
    shut_down_behavior = 'terminate'
    if main_args.cluster_name and template_name == 'app':
        shut_down_behavior = 'stop'
    instances = ec2_client.create_instances(
        ImageId=main_args.image_id,
        MinCount=run_args['count'],
        MaxCount=run_args['count'],
        InstanceType=main_args.instance_type,
        SecurityGroups=run_args['security_groups'],
        UserData=run_args['user_data'],
        BlockDeviceMappings=bdm,
        InstanceInitiatedShutdownBehavior=shut_down_behavior,
        IamInstanceProfile={
            "Name": run_args['iam_role'],
        },
        Placement={
            'AvailabilityZone': main_args.availability_zone,
        },
        KeyName=run_args['key-pair-name'],
    )
    instances_info = _wait_and_tag_instances(
        main_args,
        run_args,
        instances_tag_data,
        instances,
        main_args.image_id,
    )
    # Create aws es_wait frontend instance
    if main_args.es_wait and run_args.get('master_user_data'):
        instances = ec2_client.create_instances(
            ImageId=main_args.eshead_image_id,
            MinCount=1,
            MaxCount=1,
            InstanceType=main_args.eshead_instance_type,
            SecurityGroups=['ssh-http-https'],
            UserData=run_args['master_user_data'],
            BlockDeviceMappings=bdm,
            InstanceInitiatedShutdownBehavior='terminate',
            IamInstanceProfile={
                "Name": main_args.iam_role,
            },
            Placement={
                'AvailabilityZone': main_args.availability_zone,
            },
            KeyName=run_args['key-pair-name'],
        )
        instances_info.update(
            _wait_and_tag_instances(
                main_args,
                run_args,
                instances_tag_data,
                instances,
                main_args.eshead_image_id,
                cluster_master=True,
            )
        )
    # Displays deployment output
    print('')
    tail_cmd = " 'tail -f /var/log/cloud-init-output.log'"
    helper_vars = []
    if 'demo' in instances_info:
        instance_info = instances_info['demo']
        if main_args.build_ami:
            print('AMI Build: Demo deploying:', instance_info['name'])
            print('instance_id:', instance_info['instance_id'])
            print(
                'After it builds, create the ami: '
                "python ./cloud-config/create-ami.py {} demo {} --profile-name {}".format(
                    instances_tag_data['username'],
                    instance_info['instance_id'],
                    main_args.profile_name,
                )
            )
        else:
            print('Deploying Demo({}): {}'.format(
                instance_info['private_ip'],
                instance_info['url']
            ))
            print(" ssh ubuntu@{}".format(instance_info['instance_id_domain']))
        print("ssh and tail:\n ssh ubuntu@{}{}".format(instance_info['public_dns'], tail_cmd))
    elif 'cluster_master' in instances_info and main_args.es_wait:
        instance_info = instances_info['cluster_master']
        if main_args.build_ami:
            print('AMI Build: Wait ES cluster deploying:', instance_info['name'])
            print('instance_id:', instance_info['instance_id'])
            arg_name = 'es-wait-head'
            if main_args.es_elect:
                arg_name = 'es-elect'
            print(
                'After it builds, create the ami: '
                "python ./cloud-config/create-ami.py {} {} {} --profile-name {}".format(
                    instances_tag_data['username'],
                    arg_name,
                    instance_info['instance_id'],
                    main_args.profile_name,
                )
            )
        else:
            print('Deploying Head ES Node({}): {}'.format(
                instance_info['private_ip'],
                instance_info['name']
            ))
            print(" ssh ubuntu@{}".format(instance_info['instance_id_domain']))
        print('\nRun the following command to view es head deployment log.')
        print("ssh ubuntu@{}{}".format(instance_info['public_dns'], tail_cmd))
        print('')
        helper_vars.append("datam='{}'".format(instance_info['instance_id']))
        for index in range(main_args.cluster_size):
            str_index = str(index)
            key_name = 'cluster_node_' + str_index
            node_info = instances_info[key_name]
            helper_vars.append("data{}='{}'  # {}".format(index, node_info['instance_id'], key_name))
            if index == 0:
                if main_args.build_ami and main_args.es_wait:
                    print(
                        'After it builds, create the ami: '
                        "python ./cloud-config/create-ami.py {} es-wait-node {} --profile-name {}".format(
                            instances_tag_data['username'],
                            node_info['instance_id'],
                            main_args.profile_name,
                        )
                    )
                print('Run the following command to view this es node deployment log.')
                print("ssh ubuntu@{}{}".format(node_info['public_dns'], tail_cmd))
            else:
                print("ES node{} ssh:\n ssh ubuntu@{}".format(index, node_info['public_dns']))
    elif 'frontend' in instances_info:
        instance_info = instances_info['frontend']
        if main_args.build_ami:
            print('AMI Build: Deploying Frontend:', instance_info['name'])
            print('instance_id:', instance_info['instance_id'])
            print(
                'After it builds, create the ami: '
                "python ./cloud-config/create-ami.py {} frontend {} --profile-name {}".format(
                    instances_tag_data['username'],
                    instance_info['instance_id'],
                    main_args.profile_name,
                )
            )
        else:
            print('Deploying Frontend({}): {}'.format(
                instance_info['private_ip'],
                instance_info['url'],
            ))
            print(" ssh ubuntu@{}".format(instance_info['instance_id_domain']))
        print('\n\nRun the following command to view the deployment log.')
        print("ssh ubuntu@{}{}".format(instance_info['public_dns'], tail_cmd))
        helper_vars.append("frontend='{}'".format(instance_info['instance_id']))
    else:
        print('Warning: Unknown instance info')
        print(instances_info)
    if main_args.role == 'candidate' or main_args.build_ami:
        print('')
        # helps vars for release and building amis
        for helper_var in helper_vars:
            print(helper_var)
    print('Done')


def _parse_args():
    # pylint: disable=too-many-branches, too-many-statements

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
        if value != _nameify(value):
            raise argparse.ArgumentTypeError(
                "%r is an invalid hostname, only [a-z0-9] and hyphen allowed." % value)
        return value

    parser = argparse.ArgumentParser(
        description="Deploy ENCODE on AWS",
    )
    parser.add_argument('-b', '--branch', default=None, help="Git branch or tag")
    parser.add_argument('-n', '--name', default=None, type=hostname, help="Instance name")
    parser.add_argument('--candidate', action='store_true', help="Prod candidate Flag")
    parser.add_argument('--release-candidate', action='store_true', help="RC Flag")
    parser.add_argument('--smalldb', action='store_true', help="Only index uuids from sorted_uuid.tsv list")
    parser.add_argument(
        '--test',
        action='store_const',
        default='demo',
        const='test',
        dest='role',
        help="Set role"
    )
    parser.add_argument('--is-qa-demo', action='store_true', help="Flagged as qa demo")
    parser.add_argument(
        '--git-repo',
        default='https://github.com/ENCODE-DCC/encoded.git',
        help="Git repo to checkout branches: https://github.com/{user|org}/{repo}.git"
    )

    # User Data Yamls
    parser.add_argument('--dry-run', action='store_true', help="Exit before aws calls")
    parser.add_argument('--app-workers', default='6', help="Apache config app workers")
    parser.add_argument(
        '--conf-dir',
        default=f"{REPO_DIR}/cloud-config",
        help="Location of cloud build config"
    )
    parser.add_argument(
        '--diff-configs',
        action='store_true',
        help="Diff new build config against prebuilt."
    )
    parser.add_argument(
        '--save-config-name',
        default=None,
        help=(
            "Output cloud config to file. "
            "The type of config will be determined from args. "
            "Ex) 20190920"
        )
    )
    parser.add_argument('--use-prebuilt-config', default=None, help="Use prebuilt config file")
    parser.add_argument(
        '--region-indexer',
        default=None,
        help="Set region indexer to 'yes' or 'no'.  None is 'yes' for everything but demos."
    )
    parser.add_argument(
        '-i',
        '--identity-file',
        default="{}/.ssh/id_rsa.pub".format(expanduser("~")),
        help="ssh identity file path"
    )
    parser.add_argument(
        '--do-batchupgrade',
        default=None,
        help="Set batchupgrade to 'yes' or 'no'.  This overrides defaults if set"
    )
    parser.add_argument(
        '--batchupgrade-vars',
        nargs=4,
        default=['1000', '1', '16', '1'],
        help=(
            "Set batchupgrade vars for demo only "
            "Ex) --batchupgrade-vars 1000 1 8 1 "
            "Where the args are batchsize, chunksize, processes, and maxtasksperchild"
        )
    )
    parser.add_argument(
        '--no-indexing',
        action='store_true',
        help="Do not add indexing procs to apache"
    )
    parser.add_argument(
        '--primary-indexing',
        action='store_true',
        help="Force primary indexing"
    )
    parser.add_argument(
        '--remote-indexing',
        action='store_true',
        help="Remote indexing"
    )
    parser.add_argument(
        '--index-procs',
        default=24,
        type=int,
        help="Remote indexing"
    )
    parser.add_argument(
        '--index-chunk-size',
        default=1024,
        type=int,
        help="Should be set lower for single-node demos"
    )
    # Cluster
    parser.add_argument(
        '--es-elect',
        action='store_true',
        help="Create es nodes electing head node."
    )
    parser.add_argument('--es-wait', action='store_true', help="Create es nodes and head node.")
    parser.add_argument('--cluster-name', default=None, type=hostname, help="Name of the cluster")
    parser.add_argument('--cluster-size', type=int, default=5, help="Elasticsearch cluster size")
    parser.add_argument('--es-ip', default='localhost', help="ES Master ip address")
    parser.add_argument('--es-port', default='9201', help="ES Master ip port")
    parser.add_argument(
        '--node-name',
        default=None,
        type=hostname,
        help="Name of single node to add to already existing cluster"
    )
    parser.add_argument('--fe-ip', default='localhost', help="Primary frontend ip address")
    parser.add_argument('--jvm-gigs', default='8', help="JVM Xms and Xmx gigs")

    # Database
    parser.add_argument('--postgres-version', default='11', help="Postegres version. '9.3' or '11'")
    parser.add_argument('--pg-open', action='store_true', help="Allow all connections on postgres post.")
    parser.add_argument('--pg-ip', default='', help="Skip pg install script, setup app to connect to remote ip.")
    parser.add_argument('--redis-ip', default='localhost', help="Redis IP.")
    parser.add_argument('--redis-port', default=6379, help="Redis Port.")
    parser.add_argument('--wale-s3-prefix', default='s3://encoded-backups-prod/production-pg11')

    # AWS
    parser.add_argument('--profile-name', default='default', help="AWS creds profile")
    parser.add_argument('--iam-role', default='encoded-instance', help="Frontend AWS iam role")
    parser.add_argument('--iam-role-es', default='elasticsearch-instance', help="ES AWS iam role")
    parser.add_argument(
        '--build-ami',
        action='store_true',
        help='Flag to indicate building for ami'
    )
    parser.add_argument(
        '--full-build',
        action='store_true',
        default=True, # Defaulting to True b/c amis are more overhead than needed at the moment.
        help='Flag to indicate building without an ami'
    )
    parser.add_argument(
        '--image-id',
        help=('Demo, Frontend, and es data node override default image ami')
    )
    parser.add_argument(
        '--arm-image-id',
        action='store_true',
        help=('Override default image ami for demo to use arm')
    )
    parser.add_argument(
        '--eshead-image-id',
        help=('ES head node override default image ami')
    )
    parser.add_argument(
        '--availability-zone',
        default='us-west-2a',
        help="Set EC2 availabilty zone"
    )
    parser.add_argument(
        '--instance-type',
        help=('Demo, Frontend, and es data node override default image ami')
    )
    parser.add_argument(
        '--eshead-instance-type',
        help=('ES head node override default image ami')
    )
    parser.add_argument(
        '--volume-size',
        default=200,
        type=check_volume_size,
        help="Size of disk. Allowed values 120, 200, and 500"
    )
    parser.add_argument(
        '--no-develop-snovault',
        action="store_true",
        help=(
            "Install snovault to site-packages instead of installing editably as git "
            "repo"
        )
    )
    args = parser.parse_args()
    # Set AMI per build type
    ami_map = {
        # AWS Launch wizard: ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20200112
        'default': 'ami-0d1cd67c26f5fca19',
        'arm_default': 'ami-003b90277095b7a42',

        # Private AMIs: Add comments to each build

        # encdami-demo build on 2020-05-18 09:18:40.053861: encdami-demo-2020-05-18_091840
        'demo': 'ami-02ee743e10e6bca42',
        # encdami-es-wait-head build on 2020-05-18 15:11:07.352104: encdami-es-wait-head-2020-05-18_151107
        'es-wait-head': 'ami-04637560d9b9c4cb9',
        # encdami-es-wait-node build on 2020-05-18 15:11:07.352073: encdami-es-wait-node-2020-05-18_151107
        'es-wait-node': 'ami-03c53286feed8040f',
        #  ES elect builds were not bulit since we rarely use them
        'es-elect-head': None,
        'es-elect-node': None,
        # encdami-frontend build on 2020-05-19 06:03:16.286725: encdami-frontend-2020-05-19_060316
        'frontend': 'ami-004367e4b7cdfc264',

        # Production Private AMIs: Add comments to each build

        # encdami-es-wait-head build on 2020-05-19 06:23:26.382876: encdami-es-wait-head-2020-05-19_062326
        'es-wait-head-prod': 'ami-03530bdf05c08bf32',
        # encdami-es-wait-node build on 2020-05-19 06:23:32.339883: encdami-es-wait-node-2020-05-19_062332
        'es-wait-node-prod': 'ami-0de906a6f1894057b',
        #  ES elect builds were not bulit since we rarely use them
        'es-elect-head-prod': None,
        'es-elect-node-prod': None,
        # encdami-frontend build on 2020-05-19 06:32:47.400206: encdami-frontend-2020-05-19_063247
        'frontend-prod': 'ami-0e13a1f4c36d19ac1',
    }
    if not args.image_id:
        # Select ami by build type.  
        if args.build_ami:
            # Building new amis or making full builds from scratch
            # should start from base ubutnu image
            args.image_id = ami_map['default']
            args.eshead_image_id = ami_map['default']
            # We only need one es node to make an ami
            args.cluster_size = 1
        elif args.full_build:
            # Full builds from scratch
            # should start from base ubutnu image
            args.image_id = ami_map['default']
            args.eshead_image_id = ami_map['default']
        elif args.cluster_name:
            # Cluster builds have three prebuilt priviate amis
            if args.es_wait:
                if args.profile_name == 'production':
                    args.eshead_image_id = ami_map['es-wait-head-prod']
                    args.image_id = ami_map['es-wait-node-prod']
                else:
                    args.eshead_image_id = ami_map['es-wait-head']
                    args.image_id = ami_map['es-wait-node']
            elif args.es_elect and args.profile_name != 'production':
                if args.profile_name == 'production':
                    args.eshead_image_id = ami_map['es-elect-head-prod']
                    args.image_id = ami_map['es-elect-node-prod']
                else:
                    args.eshead_image_id = ami_map['es-elect-head']
                    args.image_id = ami_map['es-elect-node']
            else:
                if args.profile_name == 'production':
                    args.image_id = ami_map['frontend-prod']
                else:
                    args.image_id = ami_map['frontend']
        else:
            args.image_id = ami_map['demo']
    elif args.arm_image_id:
        args.image_id = ami_map['arm_default']
    else:
        args.image_id = ami_map['default']
    # Aws instance size.  If instance type is not specified, choose based on build type
    if not args.instance_type:
        if args.es_elect or args.es_wait:
            # datanode
            args.instance_type = 'm5.xlarge'
            # Head node
            args.eshead_instance_type = 'm5.xlarge'
        elif args.arm_image_id:
            # Type/Size for arm architecture
            args.instance_type = 'm6g.4xlarge'
        else:
            # frontend
            args.instance_type = 'c5.9xlarge'
    # Check cluster name overrides name
    if args.cluster_name:
        cluster_tag = '-cluster'
        cluster_name = args.cluster_name.replace(cluster_tag, '')
        args.cluster_name = cluster_name + cluster_tag
        if args.name is None:
            args.name = cluster_name
        # adding a single node to a pre existing cluster
        if args.node_name and int(args.cluster_size) != 1:
            raise ValueError(
                'Adding a node to a preexisting cluster. '
                '--cluster-size must be 1.'
            )
        # Elect clusters must have size of 4 or 5 due to
        # hard coded discovery size in es-cluster-elect.yml
        if (
                args.node_name is None and args.es_elect and (
                    int(args.cluster_size) < 4 or int(args.cluster_size) > 5
                )
        ):
            raise ValueError(
                '--es-elect cluster must have a size of 4 or 5 '
                'since election discovery is hard coded to 3 '
                'in es-cluster-elect.yml'
            )
    if args.es_wait and args.es_elect:
        raise ValueError('--es-wait and --es-elect cannot be used in the same command')
    # Set Role
    # - 'demo' role is default for making single or clustered
    # applications for feature building.
    # - '--test' will set role to test
    # - 'rc' role is for Release-Candidate QA testing and
    # is the same as 'demo' except batchupgrade will be skipped during deployment.
    # This better mimics production but require a command be run after deployment.
    # - 'candidate' role is for production release that potentially can
    # connect to produciton data.
    if not args.role == 'test':
        if args.release_candidate:
            args.role = 'rc'
            args.candidate = False
        elif args.candidate:
            args.role = 'candidate'
    # do_batchupgrade is default True for everything but rcs and candidates
    if args.do_batchupgrade is None:
        args.do_batchupgrade = 'y'
        if args.role in ['rc', 'candidate']:
            args.do_batchupgrade = 'n'
    if args.do_batchupgrade[0].lower() == 'y':
        args.do_batchupgrade = True
    else:
        args.do_batchupgrade = False
    # region_indexer is default True for everything but demos
    if args.region_indexer is not None:
        if args.region_indexer[0].lower() == 'y':
            args.region_indexer = True
        else:
            args.region_indexer = False
    elif args.role == 'demo':
        if args.smalldb:
            args.role = 'smalldb'
        args.region_indexer = False
    else:
        args.region_indexer = True
    # Add branch arg
    if not args.branch:
        args.branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        ).decode('utf-8').strip()
    # arm arch only available on demo
    if not args.role == 'demo' and args.arm_image_id:
        raise ValueError('Arm architecture is only available on demos')
    return args


if __name__ == '__main__':
    main()
