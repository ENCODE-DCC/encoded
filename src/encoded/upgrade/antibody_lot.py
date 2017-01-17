from snovault import CONNECTION
from snovault import upgrade_step
from .shared import ENCODE2_AWARDS
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

    tagged_ab = {
        'eGFP': '59c3efe9-00c6-4b1b-858b-5a208478972c',
        'YFP': '8a4e81d-3181-4332-9138-ecc39be4a3ab',
        'HA': '77d56f5a-e445-4f2c-83ac-65e00ce50ac1',
        '3XFLAG': 'f2d60a72-7b9c-422a-a80e-9493640c1d58'
    }

    context = system['context']
    registry = system['registry']
    connection = registry[CONNECTION]
    root = find_root(context)
    approvals = []

    for link_uuid in connection.get_rev_links(context.model, 'antibody', 'antibody_approval'):
        approvals.append(root.get_by_uuid(link_uuid))

    targets = set()
    for approval in approvals:
        target = root.get_by_uuid(approval.properties['target'])
        tag = target.properties['label'].split('-')[0]
        if tag in tagged_ab.keys():
            targets.add(tagged_ab[tag])
        else:
            targets.add(approval.properties['target'])
    value['targets'] = list(targets)


@upgrade_step('antibody_lot', '4', '5')
def antibody_lot_4_5(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'purifications' in value:
        value['purifications'] = list(set(value['purifications']))

    if 'targets' in value:
        value['targets'] = list(set(value['targets']))

    if 'lot_id_alias' in value:
        value['lot_id_alias'] = list(set(value['lot_id_alias']))

    if 'dbxrefs' in value:
        value['dbxrefs'] = list(set(value['dbxrefs']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))
