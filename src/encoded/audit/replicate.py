from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('replicate', frame='object')
def audit_file_platform(value, system):
    '''
    A replicate should no longer have platforms
    Should be in the schema.
    '''

    if 'platform' in value:
        detail = 'Replicate {} has a platform {}'.format(
            value['uuid'],
            value['platform']  # ['name']
            )
        yield AuditFailure('replicate with platform', detail, level='DCC_ACTION')
