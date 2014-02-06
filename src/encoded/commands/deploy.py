
import os

cfg_dir = '/etc/encoded/conf/'

def run(branch, conf, light, production, instance_name=None):
    import boto.ec2
    import time
    import sys
    import ConfigParser

    if instance_name is None:
        # Ideally we'd use the commit sha here, but only the instance knows that...
        instance_name = 'encoded/%s' % branch

    if production and light:
        print 'Invalid use of options'
        return False

    conn = boto.ec2.connect_to_region("us-west-1")
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping()
    config = ConfigParser.ConfigParser()
    config.read([conf, os.path.expanduser(cfg_dir+'snapshots.cfg'), os.path.expanduser(cfg_dir+'instance.cfg')])

    # Use appropriate EBS snapshots 
    if light:
        bdm['/dev/sdf'] = boto.ec2.blockdevicemapping.BlockDeviceType(snapshot_id=config.get('encoded.snapshots', 'pg-snap'), delete_on_termination=True)
        bdm['/dev/sdg'] = boto.ec2.blockdevicemapping.BlockDeviceType(snapshot_id=config.get('encoded.snapshots', 'es-snap'), delete_on_termination=True)
    else:
        bdm['/dev/sdf'] = boto.ec2.blockdevicemapping.BlockDeviceType(snapshot_id=config.get('encoded.snapshots', 'fm-snap'), delete_on_termination=True)
        bdm['/dev/sdg'] = boto.ec2.blockdevicemapping.BlockDeviceType(snapshot_id=config.get('encoded.snapshots', 'fm-snap'), delete_on_termination=True)

    # Use appropriate cloud config file
    if light:
        cloud_config = 'cloud-config-l.yml'
    elif production:
        cloud_config = 'cloud-config-p.yml'
    else:
        cloud_config = 'cloud-config.yml'

    user_data = open(cloud_config).read()

    user_data=user_data % {
        'AWS_ID': config.get('encoded.deploy', 'S3_ID'),
        'AWS_KEY': config.get('encoded.deploy', 'S3_KEY'),
        'AWS_SERVER': config.get('encoded.deploy', 'S3_SERVER'),
        'BRANCH': branch,
    }

    # Use 'ami-b698a9f3', 'm3.xlarge', 'sg-df30f19b' - ami from ubuntu/images/ebs/ubuntu-saucy-13.10-amd64-server-20131204
    reservation = conn.run_instances(
        config.get('encoded.instance', 'ami'),
        instance_type=config.get('encoded.instance', 'instance_type'),
        security_group_ids=[config.get('encoded.instance', 'security_group_ids')],
        user_data=user_data,
        block_device_map=bdm,
        instance_initiated_shutdown_behavior='terminate',
    )

    instance = reservation.instances[0] # Instance:i-34edd56f
    instance.add_tag('Name', instance_name) 
    instance.add_tag('branch', branch) 
    print instance
    print instance.state,

    while instance.state == 'pending':
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(1)
        instance.update()

    print
    print instance.state

    print instance.public_dns_name # u'ec2-54-219-26-167.us-west-1.compute.amazonaws.com'


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy ENCODE on AWS", 
    )

    parser.add_argument('-b', '--branch', help='Git branch or tag', default='master')
    parser.add_argument('-c', '--config', help='Configuration', default=os.path.expanduser(cfg_dir+'encoded.cfg'))
    parser.add_argument('-l', '--light', help='Use snapshot data to reduce deployment time', action="store_true")
    parser.add_argument('-n', '--name', help='Instance name')
    parser.add_argument('-p', '--production', help='Production release', action="store_true")
    args = parser.parse_args()

    return run(args.branch, args.config, args.light, args.production, args.name)


if __name__ == '__main__':
    main()
