from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
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
            detail = ('Released dataset {} contains file {} that has not been released.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('mismatched file status', detail, level='INTERNAL_ACTION')
    return


@audit_checker('Dataset', frame=['original_files'])
def audit_dataset_with_uploading_files(value, system):
    for file in value['original_files']:
        category = None
        if file['status'] in ['upload failed', 'content error']:
            category = 'file validation error'
        elif file['status'] == 'uploading':
            category = 'file in uploading state'

        if category is not None:
            detail = ('Dataset {} contains a file {} with the status {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                audit_link(path_to_text(file['@id']), file['@id']),
                file['status']
                )
            )
            yield AuditFailure(category, detail, level='ERROR')
    return
