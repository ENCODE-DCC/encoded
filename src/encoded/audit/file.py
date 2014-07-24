from ..auditor import (
    AuditFailure,
    audit_checker,
)

current_statuses = ['released', 'in progress']
not_current_statuses = ['revoked', 'obsolete', 'deleted']


@audit_checker('file')
def audit_file_status(value, system):

    file_status = value.get('status')

    if file_status == 'deleted':
        return

    if 'dataset' not in value:
        detail = 'missing dataset'
        raise AuditFailure('missing dataset', detail, level='ERROR')

    dataset_status = value['dataset']
    if 'status' not in dataset_status:
        return

#    if file_status == 'released' and dataset_status != 'released':
#        detail = '{} file - {} dataset'.format(file_status, dataset_status)
#        raise AuditFailure('status mismatch', detail, level='ERROR')

#    if file_status in current_statuses and dataset_status in not_current_statuses:
#        detail = '{} file - {} dataset'.format(file_status, dataset_status)
#        raise AuditFailure('status mismatch', detail, level='ERROR')
