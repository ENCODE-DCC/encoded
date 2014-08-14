from ..auditor import (
    AuditFailure,
    audit_checker,
)


moleculeDict = {"DNA": "SO:0000352",
                "RNA": "SO:0000356",
                "polyadenylated mRNA": "SO:0000871",
                "miRNA": "SO:0000276",
                "rRNA": "SO:0000252",
                "polyadenylated mRNA": "SO:0000871",
                "capped mRNA": "SO:0000862"
                }


@audit_checker('library')
def audit_library_nucleic_acid(value, system):
    '''
    The library needs the nucleic_acid_term_name to match the nucleic_acid_term_id
    '''
    if value['status'] == 'deleted':
        return
    if 'nucleic_acid_term_name' not in value or 'nucleic_acid_term_id' not in value:
        detail = 'library missing molecule'.format(value['accession'])
        raise AuditFailure('missing molecule', detail, level='ERROR')
    if moleculeDict[value['nucleic_acid_term_name']] != value['nucleic_acid_term_id']:
        detail = '{} - {}'.format(value['nucleic_acid_term_name'], value['nucleic_acid_term_id'])
        raise AuditFailure('molecule mismatch', detail, level='ERROR')


@audit_checker('library')
def audit_library_documents(value, system):
    '''
    If any of the library methods say <see document> then
    there needs to be a document.
    '''

    list_of_methods = ['extraction_method',
                       'fragmentation_method',
                       'library_size_selection_method',
                       'lysis_method',
                       ]
    if value['status'] == 'deleted':
        return

    for method in list_of_methods:
        if value.get(method) == "see document" and value['documents'] == []:
            detail = 'library ({}) has no document'.format(value['accession'])
            raise AuditFailure('missing document', detail, level='ERROR')


@audit_checker('library')
def audit_library_status(value, system):
    '''
    An undeleted library should have a biosample and donor that is not deleted
    A released library should have a released biosample and donor
    '''
    if value['status'] == 'deleted':
        return
    if 'biosample' not in value:
        detail = value['accession']
        raise AuditFailure('missing biosample', detail, level='ERROR')
    if value['biosample']['status'] == 'deleted':
        detail = 'library({}) has deleted biosample'.format(value['accession'])
        raise AuditFailure('status mismatch', detail, level='ERROR')
    if value['status'] == 'released':
        if value['biosample']['status'] != 'released':
            detail = value['biosample']['accession']
            raise AuditFailure('unreleased biosample', detail, level='ERROR')


@audit_checker('library')
def audit_library_RNA_size_range(value, system):
    if value['status'] == 'deleted':
        return
    if (value['nucleic_acid_term_id'] == 'SO:0000356') and ('size_range' not in value):
        detail = 'RNA libraries should have size_range specified'
        raise AuditFailure('missing size_range', detail, level='ERROR')


@audit_checker('library')
def audit_library_depleted_in(value, system):
    if value['status'] == 'deleted':
        return
    if not value['depleted_in_term_name'] or not value['depleted_in_term_id']:
        return
    for i in range(len(value['depleted_in_term_name'])):
        if value['depleted_in_term_id'][i] == value['nucleic_acid_term_id']:
            detail = '{} - {}'.format(value['depleted_in_term_name'][i], value['nucleic_acid_term_name'][i])
            yield AuditFailure('invalid depleted_in', detail, level='ERROR')

        if moleculeDict[value['depleted_in_term_name'][i]] != value['depleted_in_term_id'][i]:
            detail = '{} - {}'.format(value['depleted_in_term_name'][i], value['depleted_in_term_id'][i])
            yield AuditFailure('depleted_in term mismatch', detail, level='ERROR')
