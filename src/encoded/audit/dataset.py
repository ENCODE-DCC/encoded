from snovault import (
    AuditFailure,
    audit_checker,
)


@audit_checker('Dataset', frame='object')
def audit_dataset_release_date(value, system):
    '''
    Released experiments need release date.
    This should eventually go to schema
    '''
    if value['status'] == 'released' and 'date_released' not in value:
        detail = 'Dataset {} is released '.format(value['@id']) + \
                 'and requires a value in date_released'
        raise AuditFailure('missing date_released', detail, level='INTERNAL_ACTION')


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
