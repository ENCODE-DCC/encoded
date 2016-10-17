from snovault import upgrade_step


@upgrade_step('genetic_modification', '1', '2')
def genetic_modification_1_2(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'modifiction_description' in value:
        value['modification_description'] = value['modifiction_description']
        value.pop('modifiction_description')


@upgrade_step('genetic_modification', '2', '3')
def genetic_modification_2_3(value, system):
    # http://redmine.encodedcc.org/issues/4448
    if 'modification_description' in value:
        value['description'] = value['modification_description']
        value.pop('modification_description')

    if 'modification_zygocity' in value:
        value['zygosity'] = value['modification_zygocity']
        value.pop('modification_zygocity')

    if 'modification_purpose' in value:
        value['purpose'] = value['modification_purpose']
        value.pop('modification_purpose')

    if 'modification_genome_coordinates' in value:
        value['modified_site'] = value['modification_genome_coordinates']
        value.pop('modification_genome_coordinates')

    if 'modification_treatments' in value:
        value['treatments'] = value['modification_treatments']
        value.pop('modification_treatments')
