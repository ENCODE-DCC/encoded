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

    context = system['context']
    root = find_root(context)
    approvals = [
        root.get_by_uuid(link.source_rid)
        for link in self.model.revs
        if (link.source.item_type, link.rel) == ('antibody_approval', 'antibody')
    ]

    targets = set()
    for approval in approvals:
        target = root.get_by_uuid(approval.properties['target'])
        tag, _ = target.properties['label'].split('-', 1)
        if tag in tagged_ab:
            # need to fix logic
            target.properties['label'].split('-')[0].add(targets)
        else:
            targets.add(target.uuid)
    value['targets'] = list(targets)
