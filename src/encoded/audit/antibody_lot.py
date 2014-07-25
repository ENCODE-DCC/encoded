from ..auditor import (
    AuditFailure,
    audit_checker,
)
from pyramid.traversal import find_root


@audit_checker('antibody_lot')
def audit_antibody_lot_target(value, system):
    '''Antibody lots should not have associated characterizations for different target labels'''
    if value['status'] in ['not pursued', 'deleted']:
        return

    context = system['context']
    root = find_root(context)
    if value['targets']:
        targets = value['targets']
        first_target = root.get_by_uuid(targets[0])
        target_label = first_target['label']

        for target in targets:
            if (target['label'].startswith('eGFP-')):
                continue

            if target['label'] != target_label:
                detail = 'target mismatch for {}'.format(value['@id'])
                yield AuditFailure('target mismatch', detail, level='ERROR')
