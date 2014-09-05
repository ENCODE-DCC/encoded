from ..migrator import upgrade_step
from ..views.views import ENCODE2_AWARDS
from pyramid.traversal import find_root


@upgrade_step('antibody_lot', '', '2')
def antibody_lot_0_2(value, system):
    # http://redmine.encodedcc.org/issues/817
    value['dbxrefs'] = []

    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            new_dbxref = 'UCSC-ENCODE-cv:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']


@upgrade_step('antibody_lot', '2', '3')
def antibody_lot_2_3(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
        if value['status'] == 'DELETED':
            value['status'] = 'deleted'
        elif value['status'] == 'CURRENT':
            if value['award'] in ENCODE2_AWARDS:
                value['status'] = 'released'
            elif value['award'] not in ENCODE2_AWARDS:
                value['status'] = 'in progress'


@upgrade_step('antibody_lot', '3', '4')
def antibody_lot_3_4(value, system):
    # http://redmine.encodedcc.org/issues/380

    tagged_ab = [
        'eGFP',
        'YFP',
        'HA'
    ]

    targets = set()
    for approval_uuid in value['approvals']:
        context = system['context']
        root = find_root(context)
        approval = root.get_by_uuid(approval_uuid).upgrade_properties(finalize=False)
        target = approval.get('target')
        if target['label'].split('-')[0] in tagged_ab:
            target['label'].split('-')[0].add(targets)
        else:
            targets.add(approval.get('target'))
    value['targets'] = list(targets)
