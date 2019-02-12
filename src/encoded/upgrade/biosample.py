from snovault import upgrade_step
from .shared import ENCODE2_AWARDS, REFERENCES_UUID
from past.builtins import long
import re
from pyramid.traversal import find_root
from datetime import datetime, time


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

    # http://redmine.encodedcc.org/issues/1384
    if 'notes' in value:
        if value['notes']:
            value['notes'] = value['notes'].strip()
        else:
            del value['notes']
    if 'description' in value:
        if value['description']:
            value['description'] = value['description'].strip()
        else:
            del value['description']
    if 'submitter_comment' in value:
        if value['submitter_comment']:
            value['submitter_comment'] = value['submitter_comment'].strip()
        else:
            del value['submitter_comment']
    if 'product_id' in value:
        if value['product_id']:
            value['product_id'] = value['product_id'].strip()
        else:
            del value['product_id']
    if 'lot_id' in value:
        if value['lot_id']:
            value['lot_id'] = value['lot_id'].strip()
        else:
            del value['lot_id']

    # http://redmine.encodedcc.org/issues/2491
    if 'subcellular_fraction_term_id' in value:
        del value['subcellular_fraction_term_id']
    if 'depleted_in_term_id' in value:
        del value['depleted_in_term_id']
    if 'depleted_in_term_name' in value:
        value['depleted_in_term_name'] = list(set(value['depleted_in_term_name']))


def truncate_the_time(date_string):
    truncation_index = date_string.find('T')
    if truncation_index != -1:
        return date_string[:truncation_index]
    return date_string


@upgrade_step('biosample', '15', '16')
def biosample_15_16(value, system):
    # http://redmine.encodedcc.org/issues/5096
    # http://redmine.encodedcc.org/issues/5049
    if 'talens' in value:
        del value['talens']
    if 'pooled_from' in value and value['pooled_from'] == []:
        del value['pooled_from']

    harvest_date = value.get('culture_harvest_date')
    culture_start_date = value.get('culture_start_date')
    date_obtained = value.get('date_obtained')

    if harvest_date:
        value['culture_harvest_date'] = truncate_the_time(harvest_date)
    if culture_start_date:
        value['culture_start_date'] = truncate_the_time(culture_start_date)
    if date_obtained:
        value['date_obtained'] = truncate_the_time(date_obtained)

    if value.get('derived_from'):
        value['originated_from'] = value['derived_from']
        del value['derived_from']


@upgrade_step('biosample', '16', '17')
def biosample_16_17(value, system):
    # http://redmine.encodedcc.org/issues/5041
    if value.get('status') == 'proposed':
        value['status'] = "in progress"


@upgrade_step('biosample', '17', '18')
def biosample_17_18(value, system):
    # http://redmine.encodedcc.org/issues/4925
    return


@upgrade_step('biosample', '18', '19')
def biosample_18_19(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3507
    # https://encodedcc.atlassian.net/browse/ENCD-3536
    if 'constructs' in value:
        del value['constructs']
    if 'rnais' in value:
        del value['rnais']
    if 'transfection_type' in value:
        del value['transfection_type']
    if 'transfection_method' in value:
        del value['transfection_method']


@upgrade_step('biosample', '19', '20')
def biosample_19_20(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3848
    if value.get('biosample_type') == 'immortalized cell line':
        value['biosample_type'] = "cell line"

@upgrade_step('biosample', '20', '21')
def biosample_20_21(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3974
    return


@upgrade_step('biosample', '21', '22')
def biosample_21_22(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3555
    if value.get('biosample_type') == 'induced pluripotent stem cell line':
        value['biosample_type'] = 'cell line'
    if value.get('biosample_type') == 'stem cell':
        if value.get('biosample_term_name') in ['MSiPS', 'E14TG2a.4', 'UCSF-4', 'HUES9', 'HUES8', 'HUES66', 'HUES65',
            'HUES64', 'HUES63', 'HUES62', 'HUES6', 'HUES53', 'HUES49', 'HUES48', 'HUES45', 'HUES44', 'HUES3', 'HUES28',
            'HUES13', 'ES-I3', 'ES-E14', 'CyT49', 'BG01', 'ES-CJ7', 'WW6', 'ZHBTc4-mESC', 'ES-D3', 'H7-hESC', 'ELF-1',
            'TT2', '46C', 'ES-Bruce4', 'HUES1', 'H9', 'H1-hESC', 'BG02', 'R1', 'G1E-ER4', 'G1E']:
            value['biosample_type'] = 'cell line'
        elif value.get('biosample_term_name') in ['hematopoietic stem cell', 'embryonic stem cell',
            'mammary stem cell', 'mesenchymal stem cell of the bone marrow', "mesenchymal stem cell of Wharton's jelly",
            'mesenchymal stem cell of adipose', 'amniotic stem cell', 'stem cell of epidermis', 'mesenchymal stem cell',
            'dedifferentiated amniotic fluid mesenchymal stem cell', 'leukemia stem cell', 'neuronal stem cell',
            'neuroepithelial stem cell', 'neural stem progenitor cell']:
            value['biosample_type'] = 'primary cell'


@upgrade_step('biosample', '22', '23')
def biosample_22_23(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4360
    biosample_type_name = u'{}_{}'.format(
        value['biosample_type'], value['biosample_term_id']
    ).replace(' ', '_').replace(':', '_')
    value['biosample_ontology'] = str(
        find_root(system['context'])['biosample-types'][biosample_type_name].uuid
    )


@upgrade_step('biosample', '23', '24')
def biosample_23_24(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4420
    value.pop('biosample_type', None)
    value.pop('biosample_term_id', None)
    value.pop('biosample_term_name', None)
