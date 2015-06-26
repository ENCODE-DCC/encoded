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


def test_library_upgrade(migrator, library_1):
    value = migrator.upgrade('library', library_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_library_upgrade_status_encode3(migrator, library_1):
    library_1['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    value = migrator.upgrade('library', library_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_library_upgrade_status_deleted(migrator, library_1):
    library_1['status'] = 'DELETED'
    value = migrator.upgrade('library', library_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'


def test_library_upgrade_paired_ended(migrator, library_2):
    value = migrator.upgrade('library', library_2, target_version='4')
    assert value['schema_version'] == '4'
    assert 'paired_ended' not in value


def test_library_fragmentation(migrator, library_3):
    value = migrator.upgrade('library', library_3, target_version='4')
    assert value['schema_version'] == '4'
    assert value['fragmentation_method'] == 'shearing (Covaris generic)'
