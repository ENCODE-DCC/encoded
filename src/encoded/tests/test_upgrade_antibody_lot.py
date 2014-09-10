import pytest


@pytest.fixture
def antibody_lot_base(lab, award, source):
    return {
        'award': award['uuid'],
        'product_id': 'SAB2100398',
        'lot_id': 'QC8343',
        'lab': lab['uuid'],
        'source': source['uuid'],
    }


@pytest.fixture
def antibody_lot_1(antibody_lot_base):
    item = antibody_lot_base.copy()
    item.update({
        'schema_version': '1',
        'encode2_dbxrefs': ['CEBPZ'],
    })
    return item


@pytest.fixture
def antibody_lot_2(antibody_lot_base):
    item = antibody_lot_base.copy()
    item.update({
        'schema_version': '2',
        'award': '1a4d6443-8e29-4b4a-99dd-f93e72d42418',
        'status': "CURRENT"
    })
    return item


@pytest.fixture
def antibody_lot_3(root, antibody_lot):
    item = root.get_by_uuid(antibody_lot['uuid'])
    properties = item.properties.copy()
    del properties['targets']
    properties.update({
        'schema_version': '3'
    })
    return properties


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
    antibody_lot_2['status'] = 'DELETED'
    value = migrator.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'


def test_antibody_lot_upgrade_targets(root, registry, antibody_lot, antibody_lot_3, target, antibody_approval, threadlocals, dummy_request):
    migrator = registry['migrator']
    context = root.get_by_uuid(antibody_lot['uuid'])
    dummy_request.context = context
    value = migrator.upgrade('antibody_lot', antibody_lot_3, target_version='4', context=context)
    assert value['schema_version'] == '4'
    assert value['targets'] == [target['uuid']]
