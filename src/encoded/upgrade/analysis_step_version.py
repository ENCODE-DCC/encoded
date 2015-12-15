from contentbase import upgrade_step


@upgrade_step('analysis_step_version', '1', '2')
def analysis_step_version_1_2(value, system):

    # http://redmine.encodedcc.org/issues/3063
    if 'software_versions' in value:
        value['software_versions'] = list(set(value['software_versions']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))
