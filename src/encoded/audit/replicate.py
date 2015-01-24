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


@audit_checker('replicate', frame='embedded')
def audit_status_replicate(value, system):
    '''
    An in progress replicate should not have a released experiment
    '''

    if value['status'] > value['experiment']['status']:
        detail = 'Replicate {} has status {} while its experiment has {}'.format(
            value['uuid'],
            value['status'].
            value['experiment']['status']
            )
        yield AuditFailure('status mismatch', detail, level='DCC_ACTION')
