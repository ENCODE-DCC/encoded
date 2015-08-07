from contentbase import (
    ROOT,
    upgrade_step,
)


@upgrade_step('bismark_qc_metric', '1', '2')
def bismark_qc_metric_1_2(value, system):
    # http://redmine.encodedcc.org/issues/3114
    root = system['registry'][ROOT]
    if 'applies_to' in value:
        value['relates_to'] = value.get('applies_to')
        del value['applies_to']
