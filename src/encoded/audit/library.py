from contentbase import (
    AuditFailure,
    audit_checker,
)


@audit_checker('library', frame='object')
def audit_library_documents(value, system):
    '''
    If any of the library methods say <see document> then
    there needs to be a document.
    '''

    if value['status'] in ['deleted']:
        return

    list_of_methods = ['extraction_method',
                       'fragmentation_method',
                       'library_size_selection_method',
                       'lysis_method',
                       ]

    for method in list_of_methods:
        if value.get(method) == "see document" and value['documents'] == []:
            detail = 'Library {} method specifies "see document" yet has no document'.format(
                value['@id']
                )
            raise AuditFailure('missing documents', detail, level='NOT_COMPLIANT')
