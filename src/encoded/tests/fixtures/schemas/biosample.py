import pytest


@pytest.fixture
def biosample(testapp, source, lab, award, organism, heart):
    item = {
        'biosample_ontology': heart['uuid'],
        'source': source['@id'],
        'lab': lab['@id'],
        'award': award['@id'],
        'organism': organism['@id'],
    }
    return testapp.post_json('/biosample', item).json['@graph'][0]


@pytest.fixture
def base_biosample(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def base_mouse_biosample(testapp, lab, award, source, mouse, liver):
    item = {
        'award': award['uuid'],
        'biosample_ontology': liver['uuid'],
        'lab': lab['uuid'],
        'organism': mouse['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_1(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_2(testapp, lab, award, source, organism, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_2_liver(testapp, lab, award, source, organism, liver):
    item = {
        'award': award['uuid'],
        'biosample_ontology': liver['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]



@pytest.fixture
def biosample_ontology_slim(submitter, lab, award, source, human, brain):
    return {
        'award': award['@id'],
        'biosample_ontology': brain['uuid'],
        'lab': lab['@id'],
        'organism': human['@id'],
        'source': source['@id'],
    }


@pytest.fixture
def biosample_data(submitter, lab, award, source, organism, heart):
    return {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }

@pytest.fixture
def biosample_depleted_in(mouse_biosample, whole_organism):
    item = mouse_biosample.copy()
    item.update({
        'depleted_in_term_name': ['head'],
        'biosample_ontology': whole_organism['uuid'],
    })
    return item


@pytest.fixture
def biosample_starting_amount(biosample_data):
    item = biosample_data.copy()
    item.update({
        'starting_amount': 20
    })
    return item


@pytest.fixture
def mouse_biosample(biosample_data, mouse):
    item = biosample_data.copy()
    item.update({
        'organism': mouse['uuid'],
        'model_organism_age': '8',
        'model_organism_age_units': 'day',
        'model_organism_sex': 'female',
        'model_organism_health_status': 'apparently healthy',
        'model_organism_mating_status': 'virgin'
    })
    return item


@pytest.fixture
def mouse_whole_organism_biosample(testapp, mouse_biosample, whole_organism, transgene_insertion):
    item = mouse_biosample.copy()
    item.update({
        'biosample_ontology': whole_organism['uuid'],
        'genetic_modifications': [transgene_insertion['@id']]
    })
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_0(submitter, lab, award, source, organism):
    return {
        'award': award['uuid'],
        'biosample_term_id': 'UBERON:0000948',
        'biosample_term_name': 'heart',
        'biosample_type': 'tissue',
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid'],
    }


@pytest.fixture
def biosample_1_0(biosample_0):
    item = biosample_0.copy()
    item.update({
        'schema_version': '1',
        'starting_amount': 1000,
        'starting_amount_units': 'g'
    })
    return item


@pytest.fixture
def biosample_2_0(biosample_0):
    item = biosample_0.copy()
    item.update({
        'schema_version': '2',
        'subcellular_fraction': 'nucleus',
    })
    return item


@pytest.fixture
def biosample_3(biosample_0, biosample):
    item = biosample_0.copy()
    item.update({
        'schema_version': '3',
        'derived_from': [biosample['uuid']],
        'part_of': [biosample['uuid']],
        'encode2_dbxrefs': ['Liver'],
    })
    return item


@pytest.fixture
def biosample_4(biosample_0, encode2_award):
    item = biosample_0.copy()
    item.update({
        'schema_version': '4',
        'status': 'CURRENT',
        'award': encode2_award['uuid'],
    })
    return item


@pytest.fixture
def biosample_6(biosample_0):
    item = biosample_0.copy()
    item.update({
        'schema_version': '5',
        'sex': 'male',
        'age': '2',
        'age_units': 'week',
        'health_status': 'Normal',
        'life_stage': 'newborn',

    })
    return item


@pytest.fixture
def biosample_7(biosample_0):
    item = biosample_0.copy()
    item.update({
        'schema_version': '7',
        'worm_life_stage': 'embryonic',
    })
    return item


@pytest.fixture
def biosample_8(biosample_0):
    item = biosample_0.copy()
    item.update({
        'schema_version': '8',
        'model_organism_age': '15.0',
        'model_organism_age_units': 'day',
    })
    return item


@pytest.fixture
def biosample_9(root, biosample, publication):
    item = root.get_by_uuid(biosample['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '9',
        'references': [publication['identifiers'][0]],
    })
    return properties


@pytest.fixture
def biosample_10(root, biosample):
    item = root.get_by_uuid(biosample['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '10',
        'worm_synchronization_stage': 'starved L1 larva'
    })
    return properties


@pytest.fixture
def biosample_11(root, biosample):
    item = root.get_by_uuid(biosample['uuid'])
    properties = item.properties.copy()
    properties.update({
        'schema_version': '11',
        'dbxrefs': ['UCSC-ENCODE-cv:K562', 'UCSC-ENCODE-cv:K562'],
        'aliases': ['testing:123', 'testing:123']
    })
    return properties


@pytest.fixture
def biosample_12(biosample_0, document):
    item = biosample_0.copy()
    item.update({
        'schema_version': '12',
        'starting_amount': 'unknown',
        'starting_amount_units': 'g',
        'note': 'Value in note.',
        'submitter_comment': 'Different value in submitter_comment.',
        'protocol_documents': list(document)
    })
    return item


@pytest.fixture
def biosample_13(biosample_0, document):
    item = biosample_0.copy()
    item.update({
        'schema_version': '13',
        'notes': ' leading and trailing whitespace ',
        'description': ' leading and trailing whitespace ',
        'submitter_comment': ' leading and trailing whitespace ',
        'product_id': ' leading and trailing whitespace ',
        'lot_id': ' leading and trailing whitespace '
    })
    return item


@pytest.fixture
def biosample_15(biosample_0, biosample):
    item = biosample_0.copy()
    item.update({
        'date_obtained': '2017-06-06T20:29:37.059673+00:00',
        'schema_version': '15',
        'derived_from': biosample['uuid'],
        'talens': []
    })
    return item


@pytest.fixture
def biosample_18(biosample_0, biosample):
    item = biosample_0.copy()
    item.update({
        'biosample_term_id': 'EFO:0002067',
        'biosample_term_name': 'K562',
        'biosample_type': 'immortalized cell line',
        'transfection_type': 'stable',
        'transfection_method': 'electroporation'
    })
    return item


@pytest.fixture
def biosample_19(biosample_0, biosample):
    item = biosample_0.copy()
    item.update({
        'biosample_type': 'immortalized cell line',
    })
    return item


@pytest.fixture
def biosample_21(biosample_0, biosample):
    item = biosample_0.copy()
    item.update({
        'biosample_type': 'stem cell',
        'biosample_term_id': 'EFO:0007071',
        'biosample_term_name': 'BG01'
    })
    return item


@pytest.fixture
def biosample_human_1(testapp, lab, award, source, organism, human_donor_1, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'donor': human_donor_1['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_human_2(testapp, lab, award, source, organism, human_donor_1, heart):
    item = {
        'award': award['uuid'],
        'biosample_ontology': heart['uuid'],
        'lab': lab['uuid'],
        'donor': human_donor_1['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_22(testapp, lab, award, source, organism, epiblast):
    item = {
        'award': award['uuid'],
        'biosample_ontology': epiblast['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_23(testapp, lab, award, source, organism, epiblast):
    item = {
        'award': award['uuid'],
        'biosample_ontology': epiblast['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
        'source': source['uuid']
    }
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_pooled_from_not_characterized_biosamples(
    testapp,
    biosample_data,
    construct_genetic_modification,
    biosample_1,
    biosample_2,
):
    item = biosample_data.copy()
    item['genetic_modifications'] = [construct_genetic_modification['@id']]
    item['pooled_from'] = [biosample_1['@id'], biosample_2['@id']]
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_pooled_from_characterized_and_not_characterized_biosamples(
    testapp,
    biosample_data,
    construct_genetic_modification,
    biosample_1,
    biosample_2,
    biosample_characterization,
):
    item = biosample_data.copy()
    item['genetic_modifications'] = [construct_genetic_modification['@id']]
    item['pooled_from'] = [biosample_1['@id'], biosample_2['@id']]
    testapp.patch_json(
        biosample_characterization['@id'],
        {'characterizes': biosample_1['@id']}
    )
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_pooled_from_characterized_biosamples(
    testapp,
    biosample_data,
    construct_genetic_modification,
    biosample_1,
    biosample_2,
    biosample_characterization,
    biosample_characterization_no_review,
):
    item = biosample_data.copy()
    item['genetic_modifications'] = [construct_genetic_modification['@id']]
    item['pooled_from'] = [biosample_1['@id'], biosample_2['@id']]
    testapp.patch_json(
        biosample_characterization['@id'],
        {'characterizes': biosample_1['@id']}
    )
    testapp.patch_json(
        biosample_characterization_no_review['@id'],
        {'characterizes': biosample_2['@id']}
    )
    return testapp.post_json('/biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def biosample_with_disease(biosample_0):
    item = biosample_0.copy()
    item.update({
        'schema_version': '24',
        'disease_term_id': 'DOID:0080600'
    })
    return item
