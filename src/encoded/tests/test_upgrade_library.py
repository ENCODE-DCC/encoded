import pytest


def test_library_upgrade(upgrader, library_1_upgrade):
    value = upgrader.upgrade('library', library_1_upgrade, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_library_upgrade_status_encode3(upgrader, library_1_upgrade):
    library_1_upgrade['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    value = upgrader.upgrade('library', library_1_upgrade, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_library_upgrade_status_deleted(upgrader, library_1_upgrade):
    library_1_upgrade['status'] = 'DELETED'
    value = upgrader.upgrade('library', library_1_upgrade, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'


def test_library_upgrade_paired_ended(upgrader, library_2_upgrade):
    value = upgrader.upgrade('library', library_2_upgrade, target_version='4')
    assert value['schema_version'] == '4'
    assert 'paired_ended' not in value


def test_library_fragmentation(upgrader, library_3_upgrade):
    value = upgrader.upgrade('library', library_3_upgrade, target_version='4')
    assert value['schema_version'] == '4'
    assert value['fragmentation_method'] == 'shearing (Covaris generic)'


def test_upgrade_library_8_to_9(upgrader, library_8_upgrade):
    value = upgrader.upgrade('library', library_8_upgrade, target_version='9')
    assert value['schema_version'] == '9'
    assert isinstance(value['fragmentation_methods'], list)
    assert value['fragmentation_methods'] == ['shearing (Covaris generic)']
    assert 'fragmentation_method' not in value


def test_library_upgrade_9_to_10(upgrader, library_schema_9):
    value = upgrader.upgrade('library', library_schema_9, target_version='10')
    assert value['schema_version'] == '10'
    assert value['extraction_method'] == 'Trizol'
    assert 'lysis_method' not in value
    assert value['library_size_selection_method'] == 'gel'


def test_library_upgrade_9_to_10b(upgrader, library_schema_9b):
    value = upgrader.upgrade('library', library_schema_9b, target_version='10')
    assert value['schema_version'] == '10'
    assert value['lysis_method'] == 'other'
    assert 'test' in value['notes']
    assert 'extraction_method' not in value
