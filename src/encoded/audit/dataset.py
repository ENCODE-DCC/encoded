from snowfort import (
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
    if value['status'] in ['deleted', 'replaced', 'revoked', 'preliminary']:
        return

    if not value['references']:
        detail = 'publication dataset missing a reference to a publication'
        raise AuditFailure('missing reference', detail, level='WARNING')


@audit_checker('Dataset', frame='object')
def audit_dataset_release_date(value, system):
    '''
    Released experiments need release date.
    This should eventually go to schema
    '''
    if value['status'] == 'released' and 'date_released' not in value:
        detail = 'Dataset {} is released '.format(value['@id']) + \
                 'and requires a value in date_released'
        raise AuditFailure('missing date_released', detail, level='DCC_ACTION')
