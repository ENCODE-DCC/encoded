
from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('idr_summary_quality_metric', '2', '3')
def idr_summary_quality_metric_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3897
    # get from the file the lab and award for the attribution!!!
    conn = system['registry'][CONNECTION]
    f = conn.get_by_uuid(value['quality_metric_of'][0])
    award_uuid = str(f.properties['award'])
    lab_uuid = str(f.properties['lab'])
    award = conn.get_by_uuid(award_uuid)
    lab = conn.get_by_uuid(lab_uuid)
    value['award'] = '/awards/'+str(award.properties['name'])+'/'
    value['lab'] = '/labs/'+str(lab.properties['name'])+'/'


@upgrade_step('idr_summary_quality_metric', '3', '4')
def idr_summary_quality_metric_3_4(value, system):
    return


@upgrade_step('idr_summary_quality_metric', '4', '5')
def idr_summary_quality_metric_4_5(value, system):
    # http://redmine.encodedcc.org/issues/2491
    if 'assay_term_id' in value:
        del value['assay_term_id']

    if 'notes' in value:
        if value['notes']:
            value['notes'] = value['notes'].strip()
        else:
            del value['notes']
