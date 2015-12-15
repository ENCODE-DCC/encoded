from contentbase import upgrade_step


@upgrade_step('software_version', '1', '2')
def software_version_1_2(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))
