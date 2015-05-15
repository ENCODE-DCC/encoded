from contentbase.upgrader import upgrade_step


@upgrade_step('workflow_run', '1', '2')
def workflow_run_1_2(value, system):
    # http://redmine.encodedcc.org/issues/2922

    if 'dx_workflow_id' in value:
        value['dx_analysis_id'] = value.get('dx_workflow_id')
        del value['dx_workflow_id']
    if 'dx_workflow_json' in value:
        del value['dx_workflow_json']
