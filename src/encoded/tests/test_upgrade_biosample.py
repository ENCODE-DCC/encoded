import pytest


def test_biosample_upgrade(upgrader, biosample_1_0):
    value = upgrader.upgrade('biosample', biosample_1_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['starting_amount'] == 1000


def test_biosample_upgrade_unknown(upgrader, biosample_1_0):
    biosample_1_0['starting_amount'] = 'Unknown'
    value = upgrader.upgrade('biosample', biosample_1_0, target_version='2')
    assert value['schema_version'] == '2'
    assert 'starting_amount' not in value


def test_biosample_upgrade_empty_string(upgrader, biosample_1_0):
    biosample_1_0['starting_amount'] = ''
    value = upgrader.upgrade('biosample', biosample_1_0, target_version='2')
    assert value['schema_version'] == '2'
    assert 'starting_amount' not in value


def test_biosample_upgrade_exponent(upgrader, biosample_1_0):
    biosample_1_0['starting_amount'] = '1 X 10^5'
    value = upgrader.upgrade('biosample', biosample_1_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['starting_amount'] == 1e5


def test_biosample_upgrade_number(upgrader, biosample_1_0):
    biosample_1_0['starting_amount'] = -1
    value = upgrader.upgrade('biosample', biosample_1_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['starting_amount'] == -1


def test_biosample_upgrade_subcellular_fraction(upgrader, biosample_2_0):
    value = upgrader.upgrade('biosample', biosample_2_0, target_version='3')
    assert value['schema_version'] == '3'
    assert value['subcellular_fraction_term_name'] == 'nucleus'
    assert value['subcellular_fraction_term_id'] == 'GO:0005634'
    assert 'subcellular_fraction' not in value


def test_biosample_upgrade_subcellular_fraction_membrane(upgrader, biosample_2_0):
    biosample_2_0['subcellular_fraction'] = 'membrane fraction'
    value = upgrader.upgrade('biosample', biosample_2_0, target_version='3')
    assert value['schema_version'] == '3'
    assert value['subcellular_fraction_term_name'] == 'membrane'
    assert value['subcellular_fraction_term_id'] == 'GO:0016020'
    assert 'subcellular_fraction' not in value


def test_biosample_upgrade_array_to_string(upgrader, biosample_3, biosample):
    value = upgrader.upgrade('biosample', biosample_3, target_version='4')
    assert value['schema_version'] == '4'
    assert value['part_of'] == biosample['uuid']
    assert value['derived_from'] == biosample['uuid']


def test_biosample_upgrade_empty_array(upgrader, biosample_3, biosample):
    biosample_3['derived_from'] = []
    biosample_3['part_of'] = []
    value = upgrader.upgrade('biosample', biosample_3, target_version='4')
    assert value['schema_version'] == '4'
    assert 'part_of' not in value
    assert 'derived_from' not in value


def test_biosample_upgrade_encode2_dbxref(upgrader, biosample_3):
    value = upgrader.upgrade('biosample', biosample_3, target_version='4')
    assert value['schema_version'] == '4'
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:Liver']
    assert 'encode2_dbxrefs' not in value


def test_biosample_upgrade_encode2_complex_dbxref(upgrader, biosample_3):
    biosample_3['encode2_dbxrefs'] = ['B-cells CD20+ (RO01778)']
    value = upgrader.upgrade('biosample', biosample_3, target_version='4')
    assert value['schema_version'] == '4'
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:B-cells CD20+ (RO01778)']
    assert 'encode2_dbxrefs' not in value


def test_biosample_upgrade_status_encode2(upgrader, biosample_4):
    value = upgrader.upgrade('biosample', biosample_4, target_version='5')
    assert value['schema_version'] == '5'
    assert value['status'] == 'released'


def test_biosample_upgrade_status_encode3(upgrader, biosample_4):
    biosample_4['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    value = upgrader.upgrade('biosample', biosample_4, target_version='5')
    assert value['schema_version'] == '5'
    assert value['status'] == 'in progress'


def test_biosample_upgrade_model_organism(upgrader, biosample_6):
    value = upgrader.upgrade('biosample', biosample_6, target_version='7')
    assert value['schema_version'] == '7'
    assert 'sex' not in value
    assert 'age' not in value
    assert 'age_units' not in value
    assert 'health_status' not in value
    assert 'life_stage' not in value


def test_biosample_upgrade_model_organism_mouse(upgrader, biosample_6):
    biosample_6['organism'] = '3413218c-3d86-498b-a0a2-9a406638e786'
    value = upgrader.upgrade('biosample', biosample_6, target_version='7')
    assert value['schema_version'] == '7'
    assert 'sex' not in value
    assert value['model_organism_sex'] == 'male'
    assert 'age' not in value
    assert value['model_organism_age'] == '2'
    assert 'age_units' not in value
    assert value['model_organism_age_units'] == 'week'
    assert 'health_status' not in value
    assert value['model_organism_health_status'] == 'Normal'
    assert 'life_stage' not in value
    assert value['mouse_life_stage'] == 'postnatal'


def test_biosample_upgrade_inline(testapp, biosample_1_0, heart):
    from snovault.schema_utils import load_schema
    schema = load_schema('encoded:schemas/biosample.json')
    res = testapp.post_json('/biosample?validate=false&render=uuid', biosample_1_0)
    location = res.location

    # The properties are stored un-upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '1'

    # When the item is fetched, it is upgraded automatically.
    res = testapp.get(location).maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    res = testapp.patch_json(location, {})

    # The stored properties are now upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']


def test_biosample_upgrade_starting_amount_dep(testapp, biosample_1_0, heart):
    from snovault.schema_utils import load_schema
    schema = load_schema('encoded:schemas/biosample.json')
    biosample_1_0['starting_amount'] = 666
    biosample_1_0['starting_amount_units'] = 'g'
    res = testapp.post_json('/biosample?validate=false&render=uuid', biosample_1_0)
    location = res.location

    # The properties are stored un-upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '1'

    # When the item is fetched, it is upgraded automatically.
    res = testapp.get(location).maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    res = testapp.patch_json(location, {})

    # The stored properties are now upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    assert res.json['starting_amount'] == 666
    assert res.json['starting_amount_units'] == 'g'


def test_biosample_upgrade_starting_amount_explicit_patch(testapp, biosample_1_0, heart):
    from snovault.schema_utils import load_schema
    schema = load_schema('encoded:schemas/biosample.json')
    biosample_1_0['starting_amount'] = 0.632
    biosample_1_0['starting_amount_units'] = 'g'
    res = testapp.post_json('/biosample?validate=false&render=uuid', biosample_1_0)
    location = res.location

    # The properties are stored un-upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '1'

    # When the item is fetched, it is upgraded automatically.
    res = testapp.get(location).maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    res = testapp.patch_json(location, {'starting_amount': 0.263})

    # The stored properties are now upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    assert res.json['starting_amount'] == 0.263
    assert res.json['starting_amount_units'] == 'g'


def test_biosample_upgrade_starting_amount_unknown(testapp, biosample_1_0, heart):
    from snovault.schema_utils import load_schema
    schema = load_schema('encoded:schemas/biosample.json')
    biosample_1_0['starting_amount'] = 'unknown'
    biosample_1_0['starting_amount_units'] = 'g'
    res = testapp.post_json('/biosample?validate=false&render=uuid', biosample_1_0)
    location = res.location

    # The properties are stored un-upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == '1'

    # When the item is fetched, it is upgraded automatically.
    res = testapp.get(location).maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    res = testapp.patch_json(location, {})

    # The stored properties are now upgraded.
    res = testapp.get(location + '?frame=raw&upgrade=false').maybe_follow()
    assert res.json['schema_version'] == schema['properties']['schema_version']['default']

    assert 'starting_amount' not in res.json
    assert 'starting_amount_units' not in res.json


def test_biosample_worm_life_stage(upgrader, biosample_7):
    biosample_7['organism'] = '2732dfd9-4fe6-4fd2-9d88-61b7c58cbe20'
    value = upgrader.upgrade('biosample', biosample_7, target_version='8')
    assert value['schema_version'] == '8'
    assert value['worm_life_stage'] == 'mixed stage (embryonic)'


def test_biosample_age_pattern(upgrader, biosample_8):
    value = upgrader.upgrade('biosample', biosample_8, target_version='9')
    assert value['schema_version'] == '9'
    assert value['model_organism_age'] == '15'


def test_biosample_age_pattern2(upgrader, biosample_8):
    biosample_8['model_organism_age'] = '15.0-16.0'
    value = upgrader.upgrade('biosample', biosample_8, target_version='9')
    assert value['schema_version'] == '9'
    assert value['model_organism_age'] == '15-16'


def test_biosample_references(root, upgrader, biosample, biosample_9, publication, threadlocals, dummy_request):
    context = root.get_by_uuid(biosample['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('biosample', biosample_9, target_version='10', context=context)
    assert value['schema_version'] == '10'
    assert value['references'] == [publication['uuid']]


def test_biosample_worm_synch_stage(root, upgrader, biosample, biosample_10, dummy_request):
    context = root.get_by_uuid(biosample['uuid'])
    dummy_request.context = context
    biosample_10['organism'] = '2732dfd9-4fe6-4fd2-9d88-61b7c58cbe20'
    value = upgrader.upgrade('biosample', biosample_10, target_version='11', context=context)
    assert value['schema_version'] == '11'
    assert value['worm_synchronization_stage'] == 'L1 larva starved after bleaching'


def test_biosample_unique_array(root, upgrader, biosample, biosample_11, dummy_request):
    context = root.get_by_uuid(biosample['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('biosample', biosample_11, target_version='12', context=context)
    assert value['schema_version'] == '12'
    assert len(value['dbxrefs']) == len(set(value['dbxrefs']))
    assert len(value['aliases']) == len(set(value['aliases']))


def test_upgrade_biosample_12_to_13(root, upgrader, biosample, biosample_12, dummy_request):
    context = root.get_by_uuid(biosample['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('biosample', biosample_12, target_version='13', context=context)
    assert value['schema_version'] == '13'
    assert 'note' not in value
    assert value['submitter_comment'] == 'Different value in submitter_comment.; Value in note.'
    assert 'starting_amount_units' not in value
    assert 'starting_amount' not in value
    assert 'protocol_documents' not in value
    assert 'documents' in value


def test_upgrade_biosample_13_to_14(root, upgrader, biosample, biosample_13, dummy_request):
    context = root.get_by_uuid(biosample['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('biosample', biosample_13, target_version='14', context=context)
    assert value['schema_version'] == '14'
    assert value['notes'] == ' leading and trailing whitespace '.strip()
    assert value['submitter_comment'] == ' leading and trailing whitespace '.strip()
    assert value['description'] == ' leading and trailing whitespace '.strip()
    assert value['product_id'] == ' leading and trailing whitespace '.strip()
    assert value['lot_id'] == ' leading and trailing whitespace '.strip()


def test_upgrade_biosample_15_to_16(upgrader, biosample_15, biosample):
    value = upgrader.upgrade('biosample', biosample_15, current_version='15', target_version='16')
    assert value['originated_from'] == biosample['uuid']
    assert 'derived_from' not in value
    assert value['schema_version'] == '16'
    assert value['date_obtained'] == '2017-06-06'
    assert 'talens' not in value


def test_upgrade_biosample_18_to_19(upgrader, biosample_18, biosample):
    value = upgrader.upgrade('biosample', biosample_18, current_version='18', target_version='19')
    assert 'transfection_type' not in value
    assert 'transfection_method' not in value


def test_upgrade_biosample_19_to_20(upgrader, biosample_19, biosample):
    value = upgrader.upgrade('biosample', biosample_19, current_version='19', target_version='20')
    assert value['biosample_type'] == 'cell line'


def test_upgrade_biosample_21_to_22(upgrader, biosample_21, biosample):
    value = upgrader.upgrade('biosample', biosample_21, current_version='21', target_version='22')
    assert value['biosample_type'] == 'cell line'


def test_upgrade_biosample_22_to_23(root, upgrader, biosample_0, heart):
    value = upgrader.upgrade(
        'biosample', biosample_0, current_version='22', target_version='23',
        context=root.get_by_uuid(heart['uuid'])
    )
    assert value['biosample_ontology'] == heart['uuid']


def test_upgrade_biosample_23_to_24(upgrader, biosample_0):
    value = upgrader.upgrade(
        'biosample', biosample_0, current_version='23', target_version='24'
    )
    assert 'biosample_type' not in value
    assert 'biosample_term_id' not in value
    assert 'biosample_term_name' not in value
