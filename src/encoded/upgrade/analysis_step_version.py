from snovault import upgrade_step


@upgrade_step('analysis_step_version', '3', '4')
def analysis_step_version_3_4(value, system):
    # http://redmine.encodedcc.org/issues/4987
    if 'version' in value:
        if value['version'] > 0:
            value['minor_version'] = value['version'] - 1
        else:
            value['minor_version'] = 0
        value.pop('version', None)

    # http://redmine.encodedcc.org/issues/5050

    if value['status'] == 'replaced':
        value['status'] = 'deleted'
    return
