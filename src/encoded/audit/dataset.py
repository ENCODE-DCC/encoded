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


@audit_checker('Dataset', frame='object')
def audit_dataset_description(value, system):
    if 'description' not in value:
        return
    print ('Description = ' + value['description'])
    if value['description'].find('\\\\\\\\') != -1:
        detail = 'Dataset description text ' + \
                 'contains double backslashes.'
        yield AuditFailure('inconsistent description',
                           detail,
                           level='INTERNAL_ACTION')
