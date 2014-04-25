from pyramid.traversal import find_root
from uuid import UUID
from ..migrator import upgrade_step
import re


@upgrade_step('replicate', '', '3')
def replicate_0_3(value, system):
    # http://redmine.encodedcc.org/issues/1074
    context = system['context']
    root = find_root(context)
    if 'library' in value:
        item = root.get_by_uuid(value['library'])
        value['status'] = item.properties['status']
    else:
        value['status'] = 'in progress'
