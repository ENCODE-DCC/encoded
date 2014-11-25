from ..auditor import (
    AuditFailure,
    audit_checker,
)
from pyramid.traversal import find_root

current_statuses = ['released', 'in progress']
not_current_statuses = ['revoked', 'obsolete', 'deleted']


@audit_checker('file')
def audit_paired_with(value, system):
    '''
    A file with a paired_end needs a paired_with.
    Should be handled in the schema.
    A paired_with should be the same replicate
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if 'paired_end' not in value:
        return

    if 'paired_with' not in value:
        detail = 'File {} has paired_end = {}. It requires a value for paired_with'.format(
            value['accession'],
            value['paired_end'])
        raise AuditFailure('missing paired_with', detail, level='ERROR')

    # Would love to then check to see if the files shared the same replicate


@audit_checker('file')
def audit_file_size(value, system):

    if value['status'] in ['deleted', 'replaced', 'uploading']:
        return

    if 'file_size' not in value:
        detail = 'File {} requires a value for file_size'.format(value['accession'])
        raise AuditFailure('missing file_size', detail, level='STANDARDS_FAILURE')


@audit_checker('file')
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
