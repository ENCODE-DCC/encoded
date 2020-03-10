import pytest
from ..constants import *


@pytest.fixture
def base_antibody_characterization(testapp, lab, ENCODE3_award, target, antibody_lot, organism, k562):
    characterization_review_list = [{
        'lane': 2,
        'organism': organism['uuid'],
        'biosample_ontology': k562['uuid'],
        'lane_status': 'pending dcc review'
    }]
    item = {
        'award': ENCODE3_award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'primary_characterization_method': 'immunoblot',
        'characterization_reviews': characterization_review_list,
        'status': 'pending dcc review'
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]

@pytest.fixture
def antibody_characterization_data(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid']
    }

@pytest.fixture
def antibody_characterization(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid'],
    }

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
def base_antibody(testapp, award, lab, source, organism, target):
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


@pytest.fixture
def base_antibody_characterization1_2(testapp, lab, award, target, antibody_lot, organism, k562):
    item = {
        'award': award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'primary_characterization_method': 'immunoblot',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'characterization_reviews': [
            {
                'lane': 2,
                'organism': organism['uuid'],
                'biosample_ontology': k562['uuid'],
                'lane_status': 'compliant'
            }
        ]
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization2(testapp, lab, award, target, antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': target['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'secondary_characterization_method': 'dot blot assay',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT}
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]

@pytest.fixture
def antibody_characterization(testapp, award, lab, target, antibody_lot, attachment):
    item = {
        'characterizes': antibody_lot['@id'],
        'target': target['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
        'secondary_characterization_method': 'dot blot assay',
    }
    return testapp.post_json('/antibody_characterization', item).json['@graph'][0]


@pytest.fixture
def base_characterization_review(testapp, organism, k562):
    return {
        'lane': 2,
        'organism': organism['uuid'],
        'biosample_ontology': k562['uuid'],
        'lane_status': 'pending dcc review'
    }


@pytest.fixture
def base_characterization_review2(testapp, organism, hepg2):
    return {
        'lane': 3,
        'organism': organism['uuid'],
        'biosample_ontology': hepg2['uuid'],
        'lane_status': 'compliant'
    }

