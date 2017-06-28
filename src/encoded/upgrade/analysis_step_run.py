from snovault import (
    ROOT,
    upgrade_step,
)

'''
This upgrade is no longer needed but just kept for posterity. It no longer works after versionof: was removed as
a valid namespace in aliases. See http://redmine.encodedcc.org/issues/4748

@upgrade_step('analysis_step_run', '1', '2')
def analysis_step_run_1_2(value, system):
    # http://redmine.encodedcc.org/issues/3074
    root = system['registry'][ROOT]
    analysis_step_uuid = value.pop('analysis_step')
    analysis_step = root[analysis_step_uuid]
    analysis_step_version = root['versionof:{name}'.format(**analysis_step.properties)]
    value['analysis_step_version'] = str(analysis_step_version.uuid)

    # http://redmine.encodedcc.org/issues/3075
    if 'workflow_run' in value:
        del value['workflow_run']
'''


@upgrade_step('analysis_step_run', '3', '4')
def analysis_step_run_3_4(value, system):
    status = value.get('status')
    if status == 'error':
        value['status'] = 'deleted'
    elif status in ['waiting', 'running']:
        value['status'] = 'in progress'
    elif status == 'finished':
        value['status'] = 'released'
