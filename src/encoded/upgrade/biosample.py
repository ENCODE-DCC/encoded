from snovault import upgrade_step
from .shared import ENCODE2_AWARDS, REFERENCES_UUID
from past.builtins import long
import re
from pyramid.traversal import find_root


def number(value):
    if isinstance(value, (int, long, float, complex)):
        return value
    value = value.lower().replace(' ', '')
    value = value.replace('x10^', 'e')
    if value in ('', 'unknown'):
        return None
    try:
        return int(value)
    except ValueError:
        return float(value)


@upgrade_step('biosample', '', '2')
def biosample_0_2(value, system):
    # http://redmine.encodedcc.org/issues/794
    if 'starting_amount' in value:
        new_value = number(value['starting_amount'])
        if new_value is None:
            del value['starting_amount']
        else:
            value['starting_amount'] = new_value


@upgrade_step('biosample', '2', '3')
def biosample_2_3(value, system):
    # http://redmine.encodedcc.org/issues/940

    go_mapping = {
        "nucleus": "GO:0005634",
        "cytosol": "GO:0005829",
        "chromatin": "GO:0000785",
        "membrane": "GO:0016020",
        "membrane fraction": "GO:0016020",
        "mitochondria": "GO:0005739",
        "nuclear matrix": "GO:0016363",
        "nucleolus": "GO:0005730",
        "nucleoplasm": "GO:0005654",
        "polysome": "GO:0005844"
    }

    if 'subcellular_fraction' in value:
        value['subcellular_fraction_term_id'] = go_mapping[value['subcellular_fraction']]

        if value['subcellular_fraction'] == "membrane fraction":
            value['subcellular_fraction'] = "membrane"

        value['subcellular_fraction_term_name'] = value['subcellular_fraction']
        del value['subcellular_fraction']


@upgrade_step('biosample', '3', '4')
def biosample_3_4(value, system):
    # http://redmine.encodedcc.org/issues/575

    if 'derived_from' in value:
        if type(value['derived_from']) is list and value['derived_from']:
            new_value = value['derived_from'][0]
            value['derived_from'] = new_value
        else:
            del value['derived_from']

    if 'part_of' in value:
        if type(value['part_of']) is list and value['part_of']:
            new_value = value['part_of'][0]
            value['part_of'] = new_value
        else:
            del value['part_of']

    # http://redmine.encodedcc.org/issues/817
    value['dbxrefs'] = []

    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            new_dbxref = 'UCSC-ENCODE-cv:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']


@upgrade_step('biosample', '4', '5')
def biosample_4_5(value, system):
    # http://redmine.encodedcc.org/issues/1305
    if 'status' in value:
        if value['status'] == 'DELETED':
            value['status'] = 'deleted'
        elif value['status'] == 'CURRENT' and value['award'] in ENCODE2_AWARDS:
            value['status'] = 'released'
        elif value['status'] == 'CURRENT' and value['award'] not in ENCODE2_AWARDS:
            value['status'] = 'in progress'


@upgrade_step('biosample', '5', '6')
def biosample_5_6(value, system):
    # http://redmine.encodedcc.org/issues/1393
    if value.get('biosample_type') == 'primary cell line':
        value['biosample_type'] = 'primary cell'


@upgrade_step('biosample', '6', '7')
def biosample_6_7(value, system):
    # http://encode.stanford.edu/issues/1131

    update_properties = {
        "sex": "model_organism_sex",
        "age": "model_organism_age",
        "age_units": "model_organism_age_units",
        "health_status": "model_organism_health_status",
        "life_stage": "mouse_life_stage"
    }

    for key, val in update_properties.items():
        if key in value:
            if value["organism"] != "7745b647-ff15-4ff3-9ced-b897d4e2983c":
                if key == "life_stage" and value[key] == "newborn":
                    value[val] = "postnatal"
                else:
                    value[val] = value[key]
            del value[key]


@upgrade_step('biosample', '7', '8')
def biosample_7_8(value, system):
    # http://redmine.encodedcc.org/issues/2456

    if value.get('worm_life_stage') == 'embryonic':
        value['worm_life_stage'] = 'mixed stage (embryonic)'


@upgrade_step('biosample', '8', '9')
def biosample_8_9(value, system):
    # http://encode.stanford.edu/issues/1596

    if 'model_organism_age' in value:
        age = value['model_organism_age']
        if re.match('\d+.0(-\d+.0)?', age):
            new_age = age.replace('.0', '')
            value['model_organism_age'] = new_age


@upgrade_step('biosample', '9', '10')
def biosample_9_10(value, system):
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


@upgrade_step('biosample', '10', '11')
def biosample_10_11(value, system):
    # http://redmine.encodedcc.org/issues/2905

    if value.get('worm_synchronization_stage') == 'starved L1 larva':
        value['worm_synchronization_stage'] = 'L1 larva starved after bleaching'


@upgrade_step('biosample', '11', '12')
def biosample_11_12(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'constructs' in value:
        value['constructs'] = list(set(value['constructs']))

    if 'rnais' in value:
        value['rnais'] = list(set(value['rnais']))

    if 'talens' in value:
        value['talens'] = list(set(value['talens']))

    if 'treatments' in value:
        value['treatments'] = list(set(value['treatments']))

    if 'protocol_documents' in value:
        value['protocol_documents'] = list(set(value['protocol_documents']))

    if 'pooled_from' in value:
        value['pooled_from'] = list(set(value['pooled_from']))

    if 'dbxrefs' in value:
        value['dbxrefs'] = list(set(value['dbxrefs']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'references' in value:
        value['references'] = list(set(value['references']))


@upgrade_step('biosample', '12', '13')
def biosample_12_13(value, system):
    # http://redmine.encodedcc.org/issues/3921
    if 'note' in value:
        if 'submitter_comment' in value:
            if value['note'] != value['submitter_comment']:
                value['submitter_comment'] = value['submitter_comment'] + '; ' + value['note']
        else:
            value['submitter_comment'] = value['note']
        value.pop('note')
    # http://redmine.encodedcc.org/issues/1483#note-20
    if 'starting_amount' in value and value['starting_amount'] == 'unknown':
            value.pop('starting_amount')
            value.pop('starting_amount_units')
    if 'starting_amount_units' in value and 'starting_amount' not in value:
        value.pop('starting_amount_units')
    # http://redmine.encodedcc.org/issues/4448
    if 'protocol_documents' in value:
        value['documents'] = value['protocol_documents']
        value.pop('protocol_documents')


@upgrade_step('biosample', '13', '14')
def biosample_13_14(value, system):
    # http://redmine.encodedcc.org/issues/2491
    if 'subcellular_fraction_term_id' in value:
        del value['subcellular_fraction_term_id']
    if 'depleted_in_term_id' in value:
        del value['depleted_in_term_id']
    if 'depleted_in_term_name' in value:
        value['depleted_in_term_name'] = list(set(value['depleted_in_term_name']))
