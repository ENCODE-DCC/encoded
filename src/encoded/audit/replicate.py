from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('replicate')
def audit_file_platform(value, system):
    '''
    A replicate should no longer have flowcells or platforms
    Should be in the schema.
    '''

    if 'platform' in value:
        detail = 'Replicate {} has a platform {}'.format(
            value['uuid'],
            value['platform']['name']
            )
        yield AuditFailure('replicate with platform', detail, level='DCC_ACTION')

    if 'flowcell_details' in value and value['flowcell_details'] != []:
        detail = 'Replicate {} has flowcell_details'.format(value['uuid'])
        yield AuditFailure('replicate with flowcell', detail, level='DCC_ACTION')
