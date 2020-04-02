import pytest
from ...constants import *


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
def base_antibody_characterization1(testapp, lab, award, base_target1, antibody_lot, organism, k562, hepg2):
    item = {
        'award': award['uuid'],
        'target': base_target1['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'primary_characterization_method': 'immunoblot',
        'status': 'pending dcc review',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'characterization_reviews': [
            {
                'lane': 2,
                'organism': organism['uuid'],
                'biosample_ontology': k562['uuid'],
                'lane_status': 'pending dcc review'
            },
            {
                'lane': 3,
                'organism': organism['uuid'],
                'biosample_ontology': hepg2['uuid'],
                'lane_status': 'pending dcc review'
            }
        ]
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def base_antibody_characterization2(testapp, lab, award, base_target2, antibody_lot, organism):
    item = {
        'award': award['uuid'],
        'target': base_target2['uuid'],
        'lab': lab['uuid'],
        'characterizes': antibody_lot['uuid'],
        'secondary_characterization_method': 'dot blot assay',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT},
        'status': 'pending dcc review'
    }
    return testapp.post_json('/antibody-characterizations', item, status=201).json['@graph'][0]


@pytest.fixture
def antibody_characterization(submitter, award, lab, antibody_lot, target):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'target': target['uuid'],
        'characterizes': antibody_lot['uuid']
    }


@pytest.fixture
def antibody_characterization_url(testapp, award, lab, target, antibody_lot, attachment):
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
def biosample_characterization_base(submitter, award, lab, biosample):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'characterizes': biosample['uuid'],
    }


@pytest.fixture
def antibody_characterization_1(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '1',
        'status': 'SUBMITTED',
        'characterization_method': 'mass spectrometry after IP',
        'attachment': {'download': 'red-dot.png', 'href': RED_DOT}
    })
    return item


@pytest.fixture
def antibody_characterization_2(antibody_characterization):
    item = antibody_characterization.copy()
    item.update({
        'schema_version': '3',
        'status': 'COMPLIANT'
    })
    return item
