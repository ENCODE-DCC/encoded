from snovault import (
    AuditFailure,
    audit_checker,
)


@audit_checker('PublicationData', frame='object')
def audit_references_for_publication(value, system):
    '''
    For datasets of type publication, there should be references. Those that
    do not should be earmarked so they can be added once the publication
    has been accepted
    '''
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if not value['references']:
        detail = 'publication dataset missing a reference to a publication'
        raise AuditFailure('missing reference', detail, level='WARNING')
