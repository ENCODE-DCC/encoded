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

    root = system['root']
    if value['targets']:
        
        first_target = root.get_by_uuid(value['targets'][0])
        target_label = first_target.properties['label']

        for target_uuid in value['targets']:
            target = root.get_by_uuid(target_uuid)
            if (target.properties['label'].startswith('eGFP-')):
                continue

            if target.properties['label'] != target_label:
                detail = 'target mismatch for {}'.format(value['@id'])
                yield AuditFailure('target mismatch', detail, level='ERROR')
