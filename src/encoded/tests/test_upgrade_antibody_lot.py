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
        'schema_version': '1'
        'encode2_dbxrefs': ['CEBPZ'],
    })
    return item


 def test_antibody_lot_upgrade(app, antibody_lot_1):
    migrator = app.registry['migrator']
    value = migrator.upgrade('antibody_lot', antibody_lot_1, target_version='2')
    assert value['schema_version'] == '2'
    assert 'encode2_dbxrefs' not in value
    assert value['dbxrefs'] == ['ucsc_encode_db:CEBPZ']