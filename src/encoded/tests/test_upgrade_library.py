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
def library_4(library):
    item = library.copy()
    item.update({
        'schema_version': '4',
        'nucleic_acid_term_name': 'RNA',
        'nucleic_acid_term_id': 'SO:0000356',
        'depleted_in_term_name': ['rRNA'],
        'depleted_in_term_id': ['SO:0000252']
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


def test_library_nucleic_acid_id(upgrader, library_4):
    value = upgrader.upgrade('library', library_4, target_version='5')
    assert value['schema_version'] == '5'
    assert 'nucleic_acid_term_id' not in value


def test_library_depleted_in_id(upgrader, library_4):
    value = upgrader.upgrade('library', library_4, target_version='5')
    assert value['schema_version'] == '5'
    assert 'depleted_in_term_id' not in value
