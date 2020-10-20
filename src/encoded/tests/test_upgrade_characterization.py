import pytest


def test_antibody_characterization_upgrade(upgrader, antibody_characterization_1):
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'PENDING DCC REVIEW'
    assert value['characterization_method'] == 'immunoprecipitation followed by mass spectrometry'


def test_biosample_characterization_upgrade(upgrader, biosample_characterization_1):
    value = upgrader.upgrade('biosample_characterization', biosample_characterization_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'NOT REVIEWED'
    assert value['characterization_method'] == 'FACs analysis'


def test_antibody_characterization_upgrade_status(upgrader, antibody_characterization_2):
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_2, target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'compliant'


def test_biosample_characterization_upgrade_status_encode2(upgrader, biosample_characterization_2):
    value = upgrader.upgrade('biosample_characterization', biosample_characterization_2, target_version='4')
    assert value['schema_version'] == '4'
    assert value['status'] == 'released'


def test_antibody_characterization_upgrade_primary(upgrader, antibody_characterization_3):
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_3, target_version='5')
    assert value['schema_version'] == '5'
    assert value['primary_characterization_method'] == 'immunoblot'
    assert 'characterization_method' not in value


def test_antibody_characterization_upgrade_secondary(upgrader, antibody_characterization_3):
    antibody_characterization_3['characterization_method'] = 'immunoprecipitation followed by mass spectrometry'
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_3, target_version='5')
    assert value['schema_version'] == '5'
    assert value['secondary_characterization_method'] == 'immunoprecipitation followed by mass spectrometry'
    assert 'characterization_method' not in value


def test_antibody_characterization_upgrade_compliant_status(upgrader, antibody_characterization_3):
    antibody_characterization_3['characterization_method'] = 'immunoprecipitation followed by mass spectrometry'
    antibody_characterization_3['status'] = 'compliant'
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_3, target_version='5')
    assert value['schema_version'] == '5'
    assert value['secondary_characterization_method'] == 'immunoprecipitation followed by mass spectrometry'
    assert 'characterization_method' not in value
    assert value['reviewed_by'] == '81a6cc12-2847-4e2e-8f2c-f566699eb29e'
    assert value['documents'] == ['88dc12f7-c72d-4b43-a6cd-c6f3a9d08821']


def test_antibody_characterization_upgrade_not_compliant_status(upgrader, antibody_characterization_3):
    antibody_characterization_3['characterization_method'] = 'immunoprecipitation followed by mass spectrometry'
    antibody_characterization_3['status'] = 'not reviewed'
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_3, target_version='5')
    assert value['schema_version'] == '5'
    assert value['secondary_characterization_method'] == 'immunoprecipitation followed by mass spectrometry'
    assert 'characterization_method' not in value
    assert value['reviewed_by'] == 'ff7b77e7-bb55-4307-b665-814c9f1e65fb'


def test_biosample_characterization_upgrade_references(root, upgrader, biosample_characterization, biosample_characterization_4, publication, threadlocals, dummy_request):
    context = root.get_by_uuid(biosample_characterization['uuid'])
    dummy_request.context = context
    value = upgrader.upgrade('biosample_characterization', biosample_characterization_4,
                             target_version='5', context=context)
    assert value['schema_version'] == '5'
    assert value['references'] == [publication['uuid']]


def test_antibody_characterization_upgrade_inline(testapp, registry, antibody_characterization_1):
    from snovault import TYPES
    schema = registry[TYPES]['antibody_characterization'].schema

    res = testapp.post_json('/antibody-characterizations?validate=false&render=uuid', antibody_characterization_1)
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


def test_antibody_characterization_comment_to_submitter_comment_upgrade(upgrader, antibody_characterization_10, antibody_characterization):
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_10,
                             current_version='10', target_version='11')
    assert value['schema_version'] == '11'
    assert 'comment' not in value
    assert value['submitter_comment'] == 'We tried really hard to characterize this antibody.'


def test_upgrade_antibody_characterization_11_to_12(upgrader, antibody_characterization_11, biosample):
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_11, current_version='11', target_version='12')
    for characterization_review in value['characterization_reviews']:
        assert characterization_review['biosample_type'] == 'cell line'


def test_upgrade_antibody_characterization_13_to_14(upgrader, antibody_characterization_13, biosample):
    value = upgrader.upgrade('antibody_characterization', antibody_characterization_13, current_version='13', target_version='14')
    for characterization_review in value['characterization_reviews']:
        assert characterization_review['biosample_type'] == 'cell line'


def test_upgrade_antibody_characterization_14_to_15(root, upgrader,
                                                    antibody_characterization_14,
                                                    a549):
    value = upgrader.upgrade('antibody_characterization',
                             antibody_characterization_14,
                             current_version='14',
                             target_version='15',
                             context=root.get_by_uuid(a549['uuid']))
    for characterization_review in value['characterization_reviews']:
        assert characterization_review['biosample_ontology'] == a549['uuid']


def test_upgrade_antibody_characterization_15_to_16(upgrader,
                                                    antibody_characterization_14):
    value = upgrader.upgrade(
        'antibody_characterization', antibody_characterization_14,
        current_version='15', target_version='16'
    )
    for char_review in value['characterization_reviews']:
        assert 'biosample_type' not in char_review
        assert 'biosample_term_id' not in char_review
        assert 'biosample_term_name' not in char_review
