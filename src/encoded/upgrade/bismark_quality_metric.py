from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('bismark_quality_metric', '1', '2')
def bismark_quality_metric_1_2(value, system):
    # http://redmine.encodedcc.org/issues/3114
    conn = system['registry'][CONNECTION]
    step_run = conn.get_by_uuid(value['step_run'])
    output_files = conn.get_rev_links(step_run.model, 'step_run', 'File')
    value['quality_metric_of'] = [str(uuid) for uuid in output_files]


@upgrade_step('bismark_quality_metric', '2', '3')
def bismark_quality_metric_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'quality_metric_of' in value:
        value['quality_metric_of'] = list(set(value['quality_metric_of']))


@upgrade_step('bismark_quality_metric', '3', '4')
def bismark_quality_metric_3_4(value, system):
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


@upgrade_step('bismark_quality_metric', '4', '5')
def bismark_quality_metric_4_5(value, system):
    return


@upgrade_step('bismark_quality_metric', '5', '6')
def bismark_quality_metric_5_6(value, system):
    # http://redmine.encodedcc.org/issues/2491
    if 'assay_term_id' in value:
        del value['assay_term_id']

    if 'notes' in value:
        if value['notes']:
            value['notes'] = value['notes'].strip()
        else:
            del value['notes']
