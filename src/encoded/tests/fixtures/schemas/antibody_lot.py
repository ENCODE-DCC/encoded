import pytest


@pytest.fixture
def antibody_lot_base(testapp, mouse):
    item = {
        'product_id': 'SAB2100398',
        'lot_id': 'QC8343',
        'source': 'Acme',
        'host_organism': mouse['uuid']
    }
    return testapp.post_json('/antibody_lot', item).json['@graph'][0]
