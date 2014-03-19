from ..migrator import upgrade_step


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
        value['subcellular_fraction_term_id']  = go_mapping[value['subcellular_fraction']]
       
        if value['subcellular_fraction']== "membrane fraction":
            value['subcellular_fraction'] = "membrane"

        value['subcellular_fraction_term_name'] = value['subcellular_fraction']
        del value['subcellular_fraction']

@upgrade_step('biosample', '3', '4')
def biosample_3_4(value, system):
    # http://redmine.encodedcc.org/issues/575

    if 'derived_from' in value:
        if value['derived_from']:
            new_value = value['derived_from'][0]
            value['derived_from'] = new_value
        else:
            del value['derived_from']

    if 'part_of' in value:
        if value['part_of']:
            new_value = value['part_of'][0]
            value['part_of'] = new_value
        else:
            del value['part_of']

        

