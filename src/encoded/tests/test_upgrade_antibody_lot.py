import pytest


@pytest.fixture
def antibody_lot(lab, award, source):
    return {
        'award': award['uuid'],
        'product_id': 'SAB2100398',
        'lot_id': 'QC8343',
        'lab': lab['uuid'],
        'source': source['uuid'],
    }


@pytest.fixture
def antibody_lot_1(antibody_lot):
    item = antibody_lot.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['CEBPZ'],
    })
    return item


@pytest.fixture
def antibody_lot_2(antibody_lot):
    item = antibody_lot.copy()
    item.update({
        'schema_version': '2',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418',
        'status': "CURRENT"
    })
    return item


def test_antibody_lot_upgrade(app, antibody_lot_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_lot', antibody_lot_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:CEBPZ']


def test_antibody_lot_upgrade_status(app, antibody_lot_2):
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_antibody_lot_upgrade_status_encode3(app, antibody_lot_2):
    migrator = app.registry['migrator']
    antibody_lot_2['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f' 
    value = migrator.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_antibody_lot_upgrade_status_deleted(app, antibody_lot_2):
    migrator = app.registry['migrator']
    antibody_lot_2['status'] ='DELETED' 
    value = migrator.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'