from ..migrator import upgrade_step
from .shared import ENCODE2_AWARDS
import re
from pyramid.traversal import find_root


@upgrade_step('human_donor', '', '2')
@upgrade_step('mouse_donor', '', '2')
def donor_0_2(value, system):
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


@upgrade_step('mouse_donor', '2', '3')
def mouse_donor_2_3(value, system):
    # http://encode.stanford.edu/issues/1131

    remove_properties = [
        'sex',
        'parents',
        'children',
        'siblings',
        'fraternal_twin',
        'identical_twin'
    ]

    for remove_property in remove_properties:
        if remove_property in value:
            del value[remove_property]


@upgrade_step('human_donor', '2', '3')
def human_donor_2_3(value, system):
    # http://encode.stanford.edu/issues/1596
    if 'age' in value:
        age = value['age']
        if re.match('\d+.0(-\d+.0)?', age):
            new_age = age.replace('.0', '')
            value['age'] = new_age


@upgrade_step('human_donor', '3', '4')
@upgrade_step('mouse_donor', '3', '4')
def donor_2_3(value, system):
    # http://redmine.encodedcc.org/issues/2591
    context = system['context']
    root = find_root(context)
    publications = root['publications']
    if 'references' in value:
        new_references = []
        for ref in value['references']:
            item = publications[ref]
            new_references.append(str(item.uuid))
        value['references'] = new_references
