import pytest


@pytest.fixture
def base_antibody(award, lab, source, organism, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'targets': [target['uuid']],
        'product_id': 'KDKF123',
        'lot_id': '123'
        }


@pytest.fixture
def control_antibody(testapp, lab, award, source, mouse, target):
    item = {
        'product_id': 'WH0000468M1',
        'lot_id': 'CB191-2B3',
        'award': award['@id'],
        'lab': lab['@id'],
        'source': source['@id'],
        'host_organism': mouse['@id'],
        'control_type': 'isotype control',
        'isotype': 'IgG',
    }
    return testapp.post_json('/antibody_lot', item).json['@graph'][0]


@pytest.fixture
def tag_antibody(testapp, award, lab, source, organism, tag_target):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'targets': [tag_target['uuid']],
        'product_id': 'eGFP',
        'lot_id': '1'
    }
    return testapp.post_json('/antibodies', item, status=201).json['@graph'][0]


@pytest.fixture
def IgG_antibody(testapp, award, lab, source, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'host_organism': organism['uuid'],
        'control_type': 'isotype control',
        'isotype': 'IgG',
        'product_id': 'ABCDEF',
        'lot_id': '321'
    }
    return testapp.post_json('/antibodies', item, status=201).json['@graph'][0]
