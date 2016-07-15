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
    # http://redmine.encodedcc.org/issues/4070
    if value.get('accession') in ['ENCPL864JQQ']:
        value['group'] = 'GGR-CHIP-SEQ'
        value['version'] = 'v.tr.1'

    if value.get('accession') in ['ENCPL123UMJ']:
        value['group'] = 'GGR-RNA-SEQ'
        value['version'] = 'v.tr.1'

    if value.get('accession') in ['ENCPL660NQT']:
        value['group'] = 'GGR-DNASE-SEQ'
        value['version'] = 'v.tr.1'

    if value.get('accession') in ['ENCPL821FLJ']:
        value['group'] = 'GGR-RNA-SEQ'
        value['version'] = 'v.lg.PE.1'

    if value.get('accession') in ['ENCPL135QRQ']:
        value['group'] = 'GGR-RNA-SEQ'
        value['version'] = 'v.lg.SE.1'

    if value.get('accession') in ['ENCPL631XPY']:
        value['group'] = 'modERN-CHIP-SEQ'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL936TND',
                                  'ENCPL083VXI']:
        value['group'] = 'ENCODE-WGBS'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL985BLO',
                                  'ENCPL210QWH']:
        value['group'] = 'ENCODE-WGBS'
        value['version'] = 'v2'

    if value.get('accession') in ['ENCPL002LPE',
                                  'ENCPL337CSA',
                                  'ENCPL739VZK',
                                  'ENCPL002LSE',
                                  'ENCPL521QAX',
                                  'ENCPL611KAU',
                                  'ENCPL086BPC']:
        value['group'] = 'ENCODE-RNA-SEQ'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL184PTK']:
        value['group'] = 'ENCODE-RIP-SEQ'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL450MUC']:
        value['group'] = 'ENCODE-RAW-MAPPING'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL122WIM']:
        value['group'] = 'ENCODE-RAMPAGE'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL444CYA']:
        value['group'] = 'ENCODE-MICRO-RNA-SEQ'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL278BTI']:
        value['group'] = 'ENCODE-MICRO-RNA-COUNTS'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL357ADL']:
        value['group'] = 'ENCODE-ECLIP'
        value['version'] = ''

    if value.get('accession') in ['ENCPL654QMU',
                                  'ENCPL568PWV']:
        value['group'] = 'ENCODE-DNASE-SEQ'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL002DNS',
                                  'ENCPL001DNS']:
        value['group'] = 'ENCODE-DNASE-SEQ'
        value['version'] = 'v2'

    if value.get('accession') in ['ENCPL272XAE',
                                  'ENCPL138KID']:
        value['group'] = 'ENCODE-CHIP-SEQ'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL035XIO']:
        value['group'] = 'ENCODE-ATAC-SEQ'
        value['version'] = 'v1'

    if value.get('accession') in ['ENCPL792NWO']:
        value['group'] = 'ENCODE-ATAC-SEQ'
        value['version'] = 'v2'

    if value.get('accession') in ['ENCPL915EEO']:
        value['group'] = 'ENCODE-DNA-SEQ'
        value['version'] = 'v1'