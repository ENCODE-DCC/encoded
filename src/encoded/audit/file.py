from snovault import (
    AuditFailure,
    audit_checker,
)
from .conditions import (
    rfa,
)
from .standards_data import pipelines_with_read_depth

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


@audit_checker('file', frame='object')
def audit_file_flowcells(value, system):

    # A fastq file could have its flowcell details.


    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['file_format'] not in ['fastq']:
        return

    if 'flowcell_details' not in value or (value['flowcell_details'] == []):
        detail = 'Fastq file {} is missing flowcell_details'.format(value['@id'])
        raise AuditFailure('missing flowcell_details', detail, level='WARNING')
