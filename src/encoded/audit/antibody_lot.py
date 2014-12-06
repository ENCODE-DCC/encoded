from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('antibody_lot')
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
                value['accession'],
                char['target'],
                char['uuid'])
            yield AuditFailure('target mismatch', detail, level='ERROR')
