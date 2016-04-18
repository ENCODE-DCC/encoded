from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('samtools_stats_quality_metric', '2', '3')
def samtools_stats_quality_metric_2_3(value, system):
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
