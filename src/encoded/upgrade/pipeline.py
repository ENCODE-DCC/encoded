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


@upgrade_step('pipeline', '3', '4')
def pipeline_3_4(value, system):
    duplicates = {}

    # http://redmine.encodedcc.org/issues/3063
    if 'name' in value:
        value['step_label'] = value['name']
        value.pop('name', None)

    if 'major_version' not in value:
        # Set to 1 by default since property is required. Patch right version number afterwards.
        value['major_version'] = 1
        duplicates[value['step_label']] = 1
    else:
        value['major_version'] = duplicates[value['major_version']] + 1
        duplicates[value['major_version']] = duplicates[value['major_version']] + 1

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
