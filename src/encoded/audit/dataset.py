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
            detail = 'Released dataset {} contains file {} that has not been released.'.format(
                audit_link(value['accession'], value['@id']),
                audit_link(path_to_text(f['@id']), f['@id'])
                )
            yield AuditFailure('mismatched file status', detail, level='INTERNAL_ACTION')
    return
