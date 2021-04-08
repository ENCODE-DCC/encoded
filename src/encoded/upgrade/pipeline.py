from snovault import upgrade_step


@upgrade_step('pipeline', '', '2')
def pipeline_0_2(value, system):
    # http://redmine.encodedcc.org/issues/3001

    value['lab'] = "a558111b-4c50-4b2e-9de8-73fd8fd3a67d"  # /labs/encode-processing-pipeline/
    value['award'] = "b5736134-3326-448b-a91a-894aafb77876"  # /awards/ENCODE/


@upgrade_step('pipeline', '2', '3')
def pipeline_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3093
    value.pop('name', None)
    value.pop('version', None)
    value.pop('end_points', None)

    # http://redmine.encodedcc.org/issues/3074 note 16
    if value.get('accession') in ['ENCPL739VZK', 'ENCPL086BPC', 'ENCPL611KAU']:
        value['status'] = 'replaced'
    elif value.get('accession') == 'ENCPL521QAX':
        value['status'] = 'deleted'

    # Patch applied to upgrade pipeline objects in http://redmine.encodedcc.org/issues/3093#note-14
    # can be found in ./upgrade_data/pipeline_2_to_3_patch.json


@upgrade_step('pipeline', '3', '4')
def pipeline_3_4(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'analysis_steps' in value:
        value['analysis_steps'] = list(set(value['analysis_steps']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'references' in value:
        value['references'] = list(set(value['references']))


@upgrade_step('pipeline', '4', '5')
def pipeline_4_5(value, system):
    # http://redmine.encodedcc.org/issues/2491
    # There shouldn't be any pipelines with just assay_term_ids and not names at the time of this upgrade
    if 'assay_term_id' in value:
        del value['assay_term_id']


@upgrade_step('pipeline', '6', '7')
def pipeline_6_7(value, system):
    # http://redmine.encodedcc.org/issues/5049
    return

@upgrade_step('pipeline', '7', '8')
def pipeline_7_8(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3416
    if value.get('assay_term_name'):
        value['assay_term_names'] = [value.get('assay_term_name')]
        del value['assay_term_name']
    return


@upgrade_step('pipeline', '8', '9')
def pipeline_8_9(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3773
    if value.get('status') == 'active':
        value['status'] = 'released'


@upgrade_step('pipeline', '9', '10')
def pipeline_9_10(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4711
    for i, a in enumerate(value.get('assay_term_names', [])):
        if a == 'single-nuclei ATAC-seq':
            value['assay_term_names'][i] = 'single-nucleus ATAC-seq'


@upgrade_step('pipeline', '10', '11')
def pipeline_10_11(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5304
    for i, a in enumerate(value.get('assay_term_names', [])):
        if a == 'single cell isolation followed by RNA-seq':
            value['assay_term_names'][i] = 'single-cell RNA sequencing assay'


@upgrade_step('pipeline', '11', '12')
def pipeline_11_12(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5787
    notes = ''
    for i, a in enumerate(value.get('assay_term_names', [])):
        if a == 'single-nucleus RNA-seq':
            value['assay_term_names'][i] = 'single-cell RNA sequencing assay'
            notes += 'This pipeline is now compatible with scRNA-seq, upgraded from snRNA-seq.'
        elif a == 'genotyping by high throughput sequencing assay':
            value['assay_term_names'][i] = 'whole genome sequencing assay'
            notes += 'This pipeline is now compatible with WGS, upgraded from genotyping HTS assay.'
    if notes != '':
        if 'notes' in value:
            value['notes'] = f'{value.get("notes")}. {notes}'
        else:
            value['notes'] = notes


@upgrade_step('pipeline', '12', '13')
def pipeline_12_13(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5828
    for i, a in enumerate(value.get('assay_term_names', [])):
        if a == 'single-cell ATAC-seq':
            value['assay_term_names'][i] = 'single-nucleus ATAC-seq'
            if 'notes' in value:
                value['notes'] = f'{value.get("notes")}. This pipeline is now compatible with snATAC-seq, upgraded from scATAC-seq.'
            else:
                value['notes'] = 'This pipeline is now compatible with snATAC-seq, upgraded from scATAC-seq.'
