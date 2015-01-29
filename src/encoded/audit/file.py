from ..auditor import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa

current_statuses = ['released', 'in progress']
not_current_statuses = ['revoked', 'obsolete', 'deleted']
raw_data_formats = [
    'fastq',
    'csfasta',
    'csqual',
    'rcc',
    'idat',
    'CEL',
    ]


@audit_checker('file', frame=['replicate', 'dataset', 'replicate.experiment'])
def audit_file_replicate_match(value, system):
    '''
    A file's replicate should belong to the same experiment that the file
    does.  These tend to get confused when replacing objects.
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if 'replicate' not in value:
        return

    rep_exp = value['replicate']['experiment']['uuid']
    file_exp = value['dataset']['uuid']

    if rep_exp != file_exp:
        detail = 'File {} has a replicate {} in experiment {}'.format(
            value['accession'],
            value['replicate']['uuid'],
            value['replicate']['experiment']['accession'])
        raise AuditFailure('mismatched replicate', detail, level='ERROR')


@audit_checker('file', frame='object', condition=rfa('ENCODE3', 'FlyWormChIP'))
def audit_file_platform(value, system):
    '''
    A raw data file should have a platform specified.
    Should be in the schema.
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if value['file_format'] not in raw_data_formats:
        return

    if 'platform' not in value:
        detail = 'Raw data file {} missing platform information'.format(value['accession'])
        raise AuditFailure('missing platform', detail, level='ERROR')


@audit_checker('file',
               frame=['dataset', 'dataset.target', 'controlled_by',
                      'controlled_by.dataset'],
               condition=rfa('ENCODE2', 'ENCODE2-Mouse', 'ENCODE3', 'FlyWormChIP'))
def audit_file_controlled_by(value, system):
    '''
    A fastq in a ChIP-seq experiment should have a controlled_by
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if value['dataset'].get('assay_term_name') not in ['ChIP-seq', 'RAMPAGE', 'CAGE']:
        return

    if 'target' in value['dataset'] and value['dataset']['target'].get('investigated_as') == 'Control':
        return

    if 'controlled_by' not in value:
        value['controlled_by'] = []

    if (value['controlled_by'] == []) and (value['file_format'] in ['fastq']):
        detail = 'Fastq file {} from {} requires controlled_by'.format(
            value['accession'],
            value['dataset']['assay_term_name']
            )
        raise AuditFailure('missing controlled_by', detail, level='ERROR')

    possible_controls = value['dataset'].get('possible_controls')
    biosample = value['dataset']['biosample_term_id']

    for ff in value['controlled_by']:
        control_bs = ff['dataset']['biosample_term_id']

        if control_bs != biosample:
            detail = 'File {} has a controlled_by file {} with conflicting biosample {}'.format(
                value['accession'],
                ff['accession'],
                control_bs)
            raise AuditFailure('mismatched controlled_by', detail, level='ERROR')
            return

        if ff['file_format'] != value['file_format']:
            detail = 'File {} with file_format {} has a controlled_by file {} with file_format {}'.format(
                value['accession'],
                value['file_format'],
                ff['accession'],
                ff['file_format']
                )
            raise AuditFailure('mismatched controlled_by', detail, level='ERROR')

        if (possible_controls is None) or (ff['dataset']['@id'] not in possible_controls):
            detail = 'File {} has a controlled_by file {} with a dataset {} that is not in possible_controls'.format(
                value['accession'],
                ff['accession'],
                ff['dataset']['accession']
                )
            raise AuditFailure('mismatched controlled_by', detail, level='DCC_ACTION')


@audit_checker('file', frame='object', condition=rfa('ENCODE3', 'FlyWormChIP'))
def audit_file_flowcells(value, system):
    '''
    A fastq file could have its flowcell details.
    Don't bother to check anything but ENCODE3
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if value['file_format'] not in ['fastq']:
        return

    if 'flowcell_details' not in value or (value['flowcell_details'] == []):
        detail = 'Fastq file {} is missing flowcell_details'.format(value['accession'])
        raise AuditFailure('missing flowcell_details', detail, level='WARNING')


@audit_checker('file', frame='object')
def audit_paired_with(value, system):
    '''
    A file with a paired_end needs a paired_with.
    Should be handled in the schema.
    A paired_with should be the same replicate
    DISABLING until ticket 1795 is implemented
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if 'paired_end' not in value:
        return

    if value['paired_end'] == '1':
        context = system['context']
        paired_with = context.get_rev_links('paired_with')
        if len(paired_with) > 1:
            detail = 'Paired end 1 file {} paired_with by multiple paired end 2 files: {!r}'.format(
                value['accession'],
                paired_with,
            )
            raise AuditFailure('multiple paired_with', detail, level='ERROR')
        return

    if 'paired_with' not in value:
        detail = 'File {} has paired_end = {}. It requires a value for paired_with'.format(
            value['accession'],
            value['paired_end'])
        raise AuditFailure('missing paired_with', detail, level='DCC_ACTION')

    # Would love to then check to see if the files shared the same replicate


@audit_checker('file', frame='object')
def audit_file_size(value, system):

    if value['status'] in ['deleted', 'replaced', 'uploading']:
        return

    if 'file_size' not in value:
        detail = 'File {} requires a value for file_size'.format(value['accession'])
        raise AuditFailure('missing file_size', detail, level='DCC_ACTION')


@audit_checker('file', frame='object')
def audit_file_output_type(value, system):
    '''
    The differing RFA's will have differeing acceptable output_types
    '''

    if value.get('status') in ['deleted']:
        return

    undesirable_output_type = [
        'Base_Overlap_Signal',
        'enhancers_forebrain',
        'enhancers_heart',
        'enhancers_wholebrain',
        'Excludable',
        'ExonsDeNovo',
        'ExonsEnsV65IAcuff',
        'ExonsGencV10',
        'ExonsGencV3c',
        'ExonsGencV7',
        'FiltTransfrags',
        'GeneDeNovo',
        'GeneEnsV65IAcuff',
        'GeneGencV10',
        'GeneGencV3c',
        'GeneGencV7',
        'Junctions',
        'library_fraction',
        'Matrix',
        'mPepMapGcFt',
        'mPepMapGcUnFt'
        'PctSignal'
        'pepMapGcFt',
        'pepMapGcUnFt',
        'PrimerPeaks',
        'RbpAssocRna',
        'SumSignal',
        'TranscriptDeNovo',
        'TranscriptEnsV65IAcuff',
        'TranscriptGencV10',
        'TranscriptGencV3c',
        'TranscriptGencV7',
        'Transfrags',
        'TssGencV3c',
        'TssGencV7',
        'TssHmm',
        'UniformlyProcessedPeakCalls',
        'Validation',
        'Valleys',
        'WaveSignal',
        ]

    # if value['dataset']['award']['rfa'] != 'ENCODE3':
    if value['output_type'] in undesirable_output_type:
            detail = 'File {} has output_type "{}" which is not a standard value'.format(
                value['accession'],
                value['output_type'])
            raise AuditFailure('undesirable output_type', detail, level='DCC_ACTION')
