from snovault import upgrade_step
from .shared import ENCODE2_AWARDS, REFERENCES_UUID
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
            if re.match('doi', ref):
                new_references.append(REFERENCES_UUID[ref])
            else:
                item = publications[ref]
                new_references.append(str(item.uuid))
        value['references'] = new_references


@upgrade_step('human_donor', '4', '5')
@upgrade_step('mouse_donor', '4', '5')
def human_mouse_donor_4_5(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        unique_aliases = set(value['aliases'])
        value['aliases'] = list(unique_aliases)

    if 'dbxrefs' in value:
        unique_dbxrefs = set(value['dbxrefs'])
        value['dbxrefs'] = list(unique_dbxrefs)

    if 'references' in value:
        unique_refs = set(value['references'])
        value['references'] = list(unique_refs)

    if 'littermates' in value:
        unique_litter = set(value['littermates'])
        value['littermates'] = list(unique_litter)

    if 'parents' in value:
        unique_parents = set(value['parents'])
        value['parents'] = list(unique_parents)

    if 'children' in value:
        unique_children = set(value['children'])
        value['children'] = list(unique_children)

    if 'siblings' in value:
        unique_siblings = set(value['siblings'])
        value['siblings'] = list(unique_siblings)


@upgrade_step('fly_donor', '1', '2')
@upgrade_step('worm_donor', '1', '2')
def fly_worm_donor_1_2(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))

    if 'dbxrefs' in value:
        value['dbxrefs'] = list(set(value['dbxrefs']))

    if 'constructs' in value:
        value['constructs'] = list(set(value['constructs']))


@upgrade_step('fly_donor', '2', '3')
@upgrade_step('worm_donor', '2', '3')
@upgrade_step('human_donor', '5', '6')
@upgrade_step('mouse_donor', '5', '6')
def fly_worm_donor_2_3_and_human_mouse_5_6(value, system):
    # http://redmine.encodedcc.org/issues/3743
    if 'donor_documents' in value:
        del value['donor_documents']


@upgrade_step('fly_donor', '4', '5')
@upgrade_step('worm_donor', '4', '5')
@upgrade_step('human_donor', '7', '8')
@upgrade_step('mouse_donor', '7', '8')
def fly_worm_donor_4_5_and_human_mouse_7_8(value, system):
    # http://redmine.encodedcc.org/issues/5049
    return


@upgrade_step('fly_donor', '5', '6')
@upgrade_step('worm_donor', '5', '6')
@upgrade_step('human_donor', '8', '9')
@upgrade_step('mouse_donor', '8', '9')
def fly_worm_donor_5_6_and_human_mouse_8_9(value, system):
    # http://redmine.encodedcc.org/issues/5041
    if value.get('status') in ['preliminary', 'proposed']:
        value['status'] = "in progress"


@upgrade_step('fly_donor', '6', '7')
@upgrade_step('worm_donor', '6', '7')
@upgrade_step('mouse_donor', '9', '10')
def model_organism_donor_9_10(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3415
    value.pop('internal_tags', None)
    value.pop('littermates', None)
    value.pop('url', None)


@upgrade_step('human_donor', '9', '10')
def human_donor_9_10(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3415
    if value.get('life_stage') == 'fetal':
        value['life_stage'] = 'embryonic'
    if value.get('life_stage') == 'postnatal':
        value['life_stage'] = 'newborn'
    if not value.get('internal_tags'):
        value.pop('internal_tags', None)
    if value.get('ethnicity') in ['NA', 'Unknown', 'unknown', '']:
        value.pop('ethnicity')
    if value.get('ethnicity') == 'African-American':
        value['ethnicity'] = 'African American'
    if value.get('ethnicity') == 'African':
        value['ethnicity'] = 'Black African'
    if value.get('ethnicity') in ['caucasian', 'Caucasian/White']:
        value['ethnicity'] = 'Caucasian'
    if value.get('ethnicity') == 'Caucasian/Hispanic':
        value['ethnicity'] = 'Caucasian Hispanic'
    if value.get('ethnicity') == 'Indian/Arabian':
        value['ethnicity'] = 'Arab Indian'
    if value.get('ethnicity') == 'Asian/Hawaiian/Eskimo':
        value['ethnicity'] = 'Asian Hawaiian Eskimo'
    if value.get('fraternal_twin'):
        value['twin'] = value.get('fraternal_twin')
        value['twin_type'] = 'dizygotic'
        value.pop('fraternal_twin', None)
    if value.get('identical_twin'):
        value['twin'] = value.get('identical_twin')
        value['twin_type'] = 'monozygotic'
        value.pop('identical_twin', None)
    value.pop('children', None)
    value.pop('url', None)


@upgrade_step('fly_donor', '7', '8')
@upgrade_step('worm_donor', '7', '8')
def fly_worm_donor_7_8(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3507
    # https://encodedcc.atlassian.net/browse/ENCD-3536
    if 'constructs' in value:
        value.pop('constructs', None)
    if 'mutagen' in value:
        value.pop('mutagen', None)
    if 'mutated_gene' in value:
        value.pop('mutated_gene', None)
