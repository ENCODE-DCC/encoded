from ..migrator import upgrade_step
from ..views.views import ENCODE2_AWARDS


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

    if 'status' in value and value['status'] in ['in progress', 'released']:    
        value['status'] = 'current'

    context = system['context']
    root = find_root(context)
    targets = []
    for approval_uuid in value['approvals']:
        approval = root.get_by_uuid(approval_uuid).upgrade_properties(finalize=False)
        targets.append(approval['target'])
    value['targets'] = targets
