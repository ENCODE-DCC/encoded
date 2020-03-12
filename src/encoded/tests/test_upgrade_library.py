import pytest


@pytest.fixture
def library(lab, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
    }


@pytest.fixture
def library_1(library):
    item = library.copy()
    item.update({
        'schema_version': '2',
        'status': 'CURRENT',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418'
    })
    return item


@pytest.fixture
def library_2(library):
    item = library.copy()
    item.update({
        'schema_version': '3',
        'paired_ended': False
    })
    return item


@pytest.fixture
def library_3(library):
    item = library.copy()
    item.update({
        'schema_version': '3',
        'fragmentation_method': 'covaris sheering'
    })
    return item

@pytest.fixture
def library_8(library_3):
    item = library_3.copy()
    item.update({
        'schema_version': '8',
        'status': "in progress"
    })
    return item

def test_library_upgrade(upgrader, library_1):
    value = upgrader.upgrade('library', library_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_library_upgrade_status_encode3(upgrader, library_1):
    library_1['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    value = upgrader.upgrade('library', library_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_library_upgrade_status_deleted(upgrader, library_1):
    library_1['status'] = 'DELETED'
    value = upgrader.upgrade('library', library_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'


def test_library_upgrade_paired_ended(upgrader, library_2):
    value = upgrader.upgrade('library', library_2, target_version='4')
    assert value['schema_version'] == '4'
    assert 'paired_ended' not in value


def test_library_fragmentation(upgrader, library_3):
    value = upgrader.upgrade('library', library_3, target_version='4')
    assert value['schema_version'] == '4'
    assert value['fragmentation_method'] == 'shearing (Covaris generic)'


def test_upgrade_library_8_to_9(upgrader, library_8):
    value = upgrader.upgrade('library', library_8, target_version='9')
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
