from ..auditor import (
    AuditFailure,
    audit_checker,
)


moleculeDict = { "DNA": "SO:0000352",
                 "RNA": "SO:0000356",
                 "polyadenylated mRNA": "SO:0000871",
                 "miRNA": "SO:0000276"
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
        raise AuditFailure('mismatched molecule', detail, level='ERROR')

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
            
            
            
