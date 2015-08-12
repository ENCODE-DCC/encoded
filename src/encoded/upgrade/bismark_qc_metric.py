from contentbase import (
    ROOT,
    upgrade_step,
)

@upgrade_step('bismark_qc_metric', '1', '2')
def bismark_qc_metric_1_2(value, system):
    # http://redmine.encodedcc.org/issues/3114
    root = system['registry'][ROOT]
    step_run = root.get_by_uuid(value['step_run'])
    value['quality_metric_of'] = [str(uuid) for uuid in step_run.get_rev_links('output_files')]
