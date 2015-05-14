from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('antibody_lot', frame=[
    'characterizations',
    'characterizations.target',
])
def audit_antibody_lot_target(value, system):
    '''
    Antibody lots should not have associated characterizations
    for different target labels
    '''
    if value['status'] in ['not pursued', 'deleted']:
        return

    if not value['characterizations']:
        return

    for char in value['characterizations']:
        if char['target']['@id'] not in value['targets']:
            detail = 'The antibody_lot {} has a characterization {} with target {}, which is not in the targets list'.format(
                value['@id'],
                char['@id'],
                char['target']['@id']
                )
            yield AuditFailure('mismatched target', detail, level='ERROR')
