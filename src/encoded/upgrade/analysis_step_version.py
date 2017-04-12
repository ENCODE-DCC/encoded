from snovault import upgrade_step


@upgrade_step('analysis_step_version', '2', '3')
def analysis_step_version_2_3(value, system):
    # http://redmine.encodedcc.org/issues/4987
    if 'version' in value:
    	value['version'] = str(value['version'])
