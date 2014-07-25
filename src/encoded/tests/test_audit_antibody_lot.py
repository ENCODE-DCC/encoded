import pytest


@pytest.fixture
def base_target1(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'gene_name': 'ABCD',
        'label': 'ABCD'
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def base_target2(testapp, organism):
    item = {
        'organism': organism['uuid'],
        'gene_name': 'EFGH',
        'label': 'EFGH'
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization1(testapp, lab, award, base_target1, base_antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': base_target1['uuid'],
        'lab': lab['uuid'],
        'characterizes': base_antibody_lot['uuid'],
        'primary_characterization_method': 'immunoblot',
        'characterization_review': [
            {
                'lane': 2,
                'organism': organism['uuid'],
                'biosample_term_name': 'K562',
                'biosample_term_id': 'EFO:0002067',
                'biosample_type': 'immortalized cell line',
                'status': 'pending dcc review'
            },
            {
                'lane': 3,
                'organism': organism['uuid'],
                'biosample_term_name': 'HepG2',
                'biosample_term_id': 'EFO:0001187',
                'biosample_type': 'immortalized cell line',
                'status': 'pending dcc review'
            }
        ]
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization2(testapp, lab, award, base_target2, base_antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': base_target2['uuid'],
        'lab': lab['uuid'],
        'characterizes': base_antibody_lot['uuid'],
        'secondary_characterization_method': 'dot blot assay'
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_lot(testapp, lab, award, organism, source):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'product_id': 'ab12345',
        'lot_id': '54321',
        'host_organism': organism['uuid'],
        'status': 'pending dcc review'
    }
    return testapp.post_json('/antibody_lot', item, status=201).json['@graph'][0]


def test_audit_antibody_lot_target(testapp, base_antibody_lot, base_antibody_characterization1, base_antibody_characterization2):
    res = testapp.get(base_antibody_lot['@id'] + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'target mismatch'
