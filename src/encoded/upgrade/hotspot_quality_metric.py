from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('hotspot_quality_metric', '3', '4')
def hotspot_quality_metric_3_4(value, system):
    return


@upgrade_step('hotspot_quality_metric', '4', '5')
def hotspot_quality_metric_4_5(value, system):
    # http://redmine.encodedcc.org/issues/2491
    if 'assay_term_id' in value:
        del value['assay_term_id']

    if 'notes' in value:
        if value['notes']:
            value['notes'] = value['notes'].strip()
        else:
            del value['notes']

@upgrade_step('hotspot_quality_metric', '5', '6')
def hotspot_quality_metric_5_6(value, system):
    # http://redmine.encodedcc.org/issues/4845
    if 'SPOT score' in value:
        value['SPOT2 score'] = value['SPOT score']
        del value['SPOT score']

