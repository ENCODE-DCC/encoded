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
    return


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


@upgrade_step('antibody_lot', '5', '6')
def antibody_lot_5_6(value, system):
    # http://redmine.encodedcc.org/issues/1384
    if 'notes' in value:
        if value['notes']:
            value['notes'] = value['notes'].strip()
        else:
            del value['notes']

    if 'antigen_description' in value:
        if value['antigen_description']:
            value['antigen_description'] = value['antigen_description'].strip()
        else:
            del value['antigen_description']


@upgrade_step('antibody_lot', '7', '8')
def antibody_lot_7_8(value, system):
    # http://redmine.encodedcc.org/issues/5049
    return


@upgrade_step('antibody_lot', '8', '9')
def antibody_lot_8_9(value, system):
    # http://redmine.encodedcc.org/issues/5041
    return
