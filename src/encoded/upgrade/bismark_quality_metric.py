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
    
    #conn = system['registry'][CONNECTION]
    #if len(value['quality_metric_of']) < 1:
    value['award'] = '/awards/R01HG004456/'
    value['lab'] = '/labs/chris-burge/'
    '''
    else:
        f = conn.get_by_unique_key('accession',
                                   value['quality_metric_of'][0].split('/')[2])
        award_uuid = str(f.properties['award'])
        lab_uuid = str(f.properties['lab'])
        award = conn.get_by_uuid(award_uuid)
        lab = conn.get_by_uuid(lab_uuid)
        value['award'] = '/awards/'+str(award.properties['name'])+'/'
        value['lab'] = '/labs/'+str(lab.properties['name'])+'/'

    '''
    '''
    bigwigcorrelate_quality_metric.json V 3

    chipseq_filter_quality_metric.json V 3
    cpg_correlation_quality_metric.json V 2
    dnase_peak_quality_metric.json V 3
    edwbamstats_quality_metric.json V 3
    edwcomparepeaks_quality_metric.json V 3
    encode2_chipseq_quality_metric.json V 3
    fastqc_quality_metric.json V 3
    generic_quality_metric.json V 3

    hotspot_quality_metric.json V 3
    idr_quality_metric.json V 2
    idr_summary_quality_metric.json V 3
    
    mad_quality_metric.json V 2 
    pbc_quality_metric.json V 3
    phantompeaktools_spp_quality_metric.json V 3

    quality_metric.json ****

    samtools_flagstats_quality_metric.json V 3
    samtools_stats_quality_metric.json V 3
    star_quality_metric.json V 3
    '''