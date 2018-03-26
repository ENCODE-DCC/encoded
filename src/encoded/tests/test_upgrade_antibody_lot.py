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


@pytest.fixture
def antibody_lot_4(root, antibody_lot_3):
    item = antibody_lot_3.copy()
    item.update({
        'schema_version': '4',
        'lot_id_alias': ['testing:456', 'testing:456'],
        'purifications': ['crude', 'crude']
    })
    return item


def test_antibody_lot_upgrade(upgrader, antibody_lot_1):
    value = upgrader.upgrade('antibody_lot', antibody_lot_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['UCSC-ENCODE-cv:CEBPZ']


def test_antibody_lot_upgrade_status(upgrader, antibody_lot_2):
    value = upgrader.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'released'


def test_antibody_lot_upgrade_status_encode3(upgrader, antibody_lot_2):
    antibody_lot_2['award'] = 'ea1f650d-43d3-41f0-a96a-f8a2463d332f'
    value = upgrader.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'in progress'


def test_antibody_lot_upgrade_status_deleted(upgrader, antibody_lot_2):
    antibody_lot_2['status'] = 'DELETED'
    value = upgrader.upgrade('antibody_lot', antibody_lot_2, target_version='3')
    assert value['schema_version'] == '3'
    assert value['status'] == 'deleted'


def test_antibody_lot_unique_array(upgrader, antibody_lot_4):
    value = upgrader.upgrade('antibody_lot', antibody_lot_4, current_version='4', target_version='5')
    assert len(value['purifications']) == len(set(value['purifications']))
    assert len(value['lot_id_alias']) == len(set(value['lot_id_alias']))
