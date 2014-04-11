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


def test_library_upgrade(app, library_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('library', library_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_library_upgrade_status_encode3(app, library_1):
    migrator = app.registry['migrator']
    library_1['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    value = migrator.upgrade('library', library_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_library_upgrade_status_deleted(app, library_1):
    migrator = app.registry['migrator']
    library_1['status'] = 'DELETED'
    value = migrator.upgrade('library', library_1, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'
    