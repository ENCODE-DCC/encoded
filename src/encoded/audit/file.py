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
        'Alignability',
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
        'HMM',
        'Junctions',
        'library_fraction',
        'Matrix',
        'minus signal',
        'mPepMapGcFt',
        'mPepMapGcUnFt'
        'PctSignal'
        'pepMapGcFt',
        'pepMapGcUnFt',
        'Primer',
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
        'Uniqueness',
        'Validation',
        'Valleys',
        'WaveSignal',
        ]

    # if value['dataset']['award']['rfa'] != 'ENCODE3':
    if value['output_type'] in undesirable_output_type:
            detail = 'File {} has output_type "{}" which is not a standard value'.format(
                value['accession'],
                value['output_type'])
            raise AuditFailure('undesirable output type', detail, level='DCC_ACTION')
