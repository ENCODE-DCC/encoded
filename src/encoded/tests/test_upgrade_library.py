import pytest


def test_library_upgrade(upgrader, library_1_0):
    value = upgrader.upgrade('library', library_1_0, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_library_upgrade_status_encode3(upgrader, library_1_0):
    library_1_0['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    value = upgrader.upgrade('library', library_1_0, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_library_upgrade_status_deleted(upgrader, library_1_0):
    library_1_0['status'] = 'DELETED'
    value = upgrader.upgrade('library', library_1_0, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'


def test_library_upgrade_paired_ended(upgrader, library_2_0):
    value = upgrader.upgrade('library', library_2_0, target_version='4')
    assert value['schema_version'] == '4'
    assert 'paired_ended' not in value


def test_library_fragmentation(upgrader, library_3_0):
    value = upgrader.upgrade('library', library_3_0, target_version='4')
    assert value['schema_version'] == '4'
    assert value['fragmentation_method'] == 'shearing (Covaris generic)'


def test_upgrade_library_8_to_9(upgrader, library_8_0):
    value = upgrader.upgrade('library', library_8_0, target_version='9')
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


def test_library_upgrade_10_to_11(upgrader, library_schema_10):
    value = upgrader.upgrade('library', library_schema_10, target_version='11')
    assert value['schema_version'] == '11'
    assert value['strand_specificity'] == 'strand-specific'


def test_library_upgrade_11_to_12(upgrader, library_schema_11a, library_schema_11b):
    value = upgrader.upgrade('library', library_schema_11a, target_version='12')
    assert value['schema_version'] == '12'
    assert 'shearing (generic)' in value['fragmentation_methods']
    assert 'chemical (DpnII restriction)' in value['fragmentation_methods']
    assert 'chemical (HindIII restriction)' in value['fragmentation_methods']
    assert 'chemical (HindIII/DpnII restriction)' not in value['fragmentation_methods']

    # library with both dual and single restriction enzyme in fragmentation_methods
    value = upgrader.upgrade('library', library_schema_11b, target_version='12')
    assert value['schema_version'] == '12'
    assert 'shearing (generic)' in value['fragmentation_methods']
    assert 'chemical (DpnII restriction)' in value['fragmentation_methods']
    assert 'chemical (HindIII restriction)' in value['fragmentation_methods']
    assert 'chemical (HindIII/DpnII restriction)' not in value['fragmentation_methods']


def test_library_upgrade_12_to_13(upgrader, library_schema_12):
    value = upgrader.upgrade('library', library_schema_12, target_version='13')
    assert value['schema_version'] == '13'
    assert value['adapters'][0]['type'] == 'read1 3\' adapter'
    assert value['adapters'][1]['type'] == 'unspecified adapter'


def test_library_upgrade_13_to_14(upgrader, library_schema_13):
    value = upgrader.upgrade('library', library_schema_13, target_version='14')
    assert value['schema_version'] == '14'
    assert value['nucleic_acid_term_name'] == 'RNA'
    assert value['notes'] == 'The nucleic_acid_term_name of this library was automatically upgraded by ENCD-5368.'


def test_library_upgrade_14_to_15(upgrader, library_schema_14):
    value = upgrader.upgrade('library', library_schema_14, current_version='14', target_version='15')
    assert value['schema_version'] == '15'
    assert value['nucleic_acid_term_name'] == 'RNA'
    assert value['notes'] == 'The nucleic_acid_term_name of this library was automatically upgraded by ENCD-5647.'
