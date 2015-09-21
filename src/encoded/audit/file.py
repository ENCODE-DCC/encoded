from contentbase import (
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

paired_end_assays = [
    'RNA-PET',
    'ChIA-PET',
    'DNA-PET',
    ]


@audit_checker('file', frame=['replicate', 'dataset', 'replicate.experiment'])
def audit_file_replicate_match(value, system):
    '''
    A file's replicate should belong to the same experiment that the file
    does.  These tend to get confused when replacing objects.
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'replicate' not in value:
        return

    rep_exp = value['replicate']['experiment']['uuid']
    file_exp = value['dataset']['uuid']

    if rep_exp != file_exp:
        detail = 'File {} has a replicate {} in experiment {}'.format(
            value['@id'],
            value['replicate']['@id'],
            value['replicate']['experiment']['@id'])
        raise AuditFailure('mismatched replicate', detail, level='ERROR')


@audit_checker('file', frame='object', condition=rfa('ENCODE3', 'modERN', 'ENCODE2', 'ENCODE2-Mouse'))
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
        detail = 'Raw data file {} missing platform information'.format(value['@id'])
        raise AuditFailure('missing platform', detail, level='ERROR')


@audit_checker('file', frame='object', condition=rfa('ENCODE3', 'modERN', 'ENCODE2', 'ENCODE2-Mouse'))
def audit_file_read_length(value, system):
    '''
    Reads files should have a read_length
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['output_type'] != 'reads':
        return

    if 'read_length' not in value:
        detail = 'Reads file {} missing read_length'.format(value['@id'])
        raise AuditFailure('missing read_length', detail, level='ERROR')


@audit_checker('file',
               frame=['dataset', 'dataset.target', 'controlled_by',
                      'controlled_by.dataset'],
               condition=rfa('ENCODE2', 'ENCODE2-Mouse', 'ENCODE3', 'modERN'))
def audit_file_controlled_by(value, system):
    '''
    A fastq in a ChIP-seq experiment should have a controlled_by
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['dataset'].get('assay_term_name') not in ['ChIP-seq', 'RAMPAGE', 'CAGE', 'shRNA knockdown followed by RNA-seq']:
        return

    if 'target' in value['dataset'] and 'control' in value['dataset']['target'].get('investigated_as', []):
        return

    if 'controlled_by' not in value:
        value['controlled_by'] = []

    if (value['controlled_by'] == []) and (value['file_format'] in ['fastq']):
        detail = 'Fastq file {} from {} requires controlled_by'.format(
            value['@id'],
            value['dataset']['assay_term_name']
            )
        raise AuditFailure('missing controlled_by', detail, level='NOT_COMPLIANT')

    possible_controls = value['dataset'].get('possible_controls')
    biosample = value['dataset'].get('biosample_term_id')

    for ff in value['controlled_by']:
        control_bs = ff['dataset'].get('biosample_term_id')

        if control_bs != biosample:
            detail = 'File {} has a controlled_by file {} with conflicting biosample {}'.format(
                value['@id'],
                ff['@id'],
                control_bs)
            raise AuditFailure('mismatched controlled_by', detail, level='ERROR')
            return

        if ff['file_format'] != value['file_format']:
            detail = 'File {} with file_format {} has a controlled_by file {} with file_format {}'.format(
                value['@id'],
                value['file_format'],
                ff['@id'],
                ff['file_format']
                )
            raise AuditFailure('mismatched controlled_by', detail, level='ERROR')

        if (possible_controls is None) or (ff['dataset']['@id'] not in possible_controls):
            detail = 'File {} has a controlled_by file {} with a dataset {} that is not in possible_controls'.format(
                value['@id'],
                ff['@id'],
                ff['dataset']['@id']
                )
            raise AuditFailure('mismatched controlled_by', detail, level='DCC_ACTION')


@audit_checker('file', frame='object', condition=rfa('ENCODE3', 'modERN'))
def audit_file_flowcells(value, system):
    '''
    A fastq file could have its flowcell details.
    Don't bother to check anything but ENCODE3
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['file_format'] not in ['fastq']:
        return

    if 'flowcell_details' not in value or (value['flowcell_details'] == []):
        detail = 'Fastq file {} is missing flowcell_details'.format(value['@id'])
        raise AuditFailure('missing flowcell_details', detail, level='WARNING')


@audit_checker('file', frame=['paired_with'],)
def audit_paired_with(value, system):
    '''
    A file with a paired_end needs a paired_with.
    Should be handled in the schema.
    A paired_with should be the same replicate
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'paired_end' not in value:
        return

    if 'paired_with' not in value:
        detail = 'File {} has paired_end = {}. It requires a paired file'.format(
            value['@id'],
            value['paired_end'])
        raise AuditFailure('missing paired_with', detail, level='NOT_COMPLIANT')

    if 'replicate' not in value['paired_with']:
        return

    if 'replicate' not in value:
        detail = 'File {} has paired_end = {}. It requires a replicate'.format(
            value['@id'],
            value['paired_end'])
        raise AuditFailure('missing replicate', detail, level='DCC_ACTION')

    if value['replicate'] != value['paired_with']['replicate']:
        detail = 'File {} has replicate {}. It is paired_with file {} with replicate {}'.format(
            value['@id'],
            value.get('replicate'),
            value['paired_with']['@id'],
            value['paired_with'].get('replicate'))
        raise AuditFailure('mismatched paired_with', detail, level='ERROR')

    if value['paired_end'] == '1':
        context = system['context']
        paired_with = context.get_rev_links('paired_with')
        if len(paired_with) > 1:
            detail = 'Paired end 1 file {} paired_with by multiple paired end 2 files: {!r}'.format(
                value['@id'],
                paired_with,
            )
            raise AuditFailure('multiple paired_with', detail, level='ERROR')


@audit_checker('file', frame='object')
def audit_file_size(value, system):

    if value['status'] in ['deleted', 'replaced', 'uploading', 'revoked']:
        return

    if 'file_size' not in value:
        detail = 'File {} requires a value for file_size'.format(value['@id'])
        raise AuditFailure('missing file_size', detail, level='DCC_ACTION')


@audit_checker('file', frame=['file_format_specifications'],)
def audit_file_format_specifications(value, system):

    for doc in value.get('file_format_specifications', []):
        if doc['document_type'] != "file format specification":
            detail = 'File {} has document {} not of type file format specification'.format(
                value['@id'],
                doc['@id']
                )
            raise AuditFailure('wrong document_type', detail, level='ERROR')


@audit_checker('file', frame='object')
def audit_file_paired_ended_run_type(value, system):
    '''
    Audit to catch those files that were upgraded to have run_type = paired ended
    resulting from its migration out of replicate but lack the paired_end property
    to specify which read it is. This audit will also catch the case where run_type
    = paired-ended but there is no paired_end = 2 due to registeration error.
    '''

    if value['status'] in ['deleted', 'replaced', 'revoked', 'upload failed']:
        return

    if value['file_format'] not in ['fastq', 'fasta', 'csfasta']:
        return

    if (value['output_type'] == 'reads') and (value.get('run_type') == 'paired-ended'):
        if 'paired_end' not in value:
            detail = 'File {} has a paired-ended run_type but is missing its paired_end value'.format(
                value['@id'])
            raise AuditFailure('missing paired_end', detail, level='DCC_ACTION')

        if (value['paired_end'] == 1) and 'paired_with' not in value:
            detail = 'File {} has a paired-ended run_type but is missing a paired_end=2 mate'.format(
                value['@id'])
            raise AuditFailure('missing mate pair', detail, level='DCC_ACTION')
