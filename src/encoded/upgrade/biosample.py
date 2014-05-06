from ..migrator import upgrade_step
from ..views.views import ENCODE2_AWARDS


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
    # http://encode.stanford.edu/issues/1131

    update_properties = {
        "sex": "model_organism_sex",
        "age": "model_organism_age",
        "age_units": "model_organism_age_units",
        "health_status": "model_organism_health_status",
        "life_stage": "model_organism_life_stage"
    }

    for key, val in update_properties.items():
        if key in value:
            if value["organism"] != "7745b647-ff15-4ff3-9ced-b897d4e2983c":
                value[val] = value[key]
            del value[key]