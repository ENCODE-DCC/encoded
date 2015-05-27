from contentbase.upgrader import upgrade_step
from pyramid.traversal import find_root


@upgrade_step('replicate', '', '3')
def replicate_0_3(value, system):
    # http://redmine.encodedcc.org/issues/1074
    context = system['context']
    root = find_root(context)
    if 'library' in value:
        library = root.get_by_uuid(value['library']).upgrade_properties()
        value['status'] = library['status']
    else:
        value['status'] = 'in progress'

    # http://redmine.encodedcc.org/issues/1354
    if 'paired_ended' in value and 'read_length' not in value:
        del value['paired_ended']


@upgrade_step('replicate', '3', '4')
def replicate_3_4(value, system):
    # http://redmine.encodedcc.org/issues/2498
    if 'flowcell_details' in value:
        if len(value['flowcell_details']) > 0:
            details = repr(value['flowcell_details'])
            if 'notes' in value:
                value['notes'] = value['notes'] + details
            else:
                value['notes'] = details
        del value['flowcell_details']
