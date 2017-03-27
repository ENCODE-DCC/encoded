from snovault import (
    AuditFailure,
    audit_checker,
)


@audit_checker('Dataset', frame=['original_files'])
def audit_experiment_released_with_unreleased_files(value, system):
    if value['status'] != 'released':
        return
    if 'original_files' not in value:
        return
    for f in value['original_files']:
        if f['status'] not in ['released', 'deleted',
                               'revoked', 'replaced',
                               'archived']:
            detail = 'Released dataset {} '.format(value['@id']) + \
                     'contains file  {} '.format(f['@id']) + \
                     'that has not been released.'
            yield AuditFailure('mismatched file status', detail, level='INTERNAL_ACTION')
    return
