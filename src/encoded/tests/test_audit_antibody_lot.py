import pytest

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""


@pytest.fixture
def base_target1(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'label': 'ABCD',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


@pytest.fixture
def base_target2(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'label': 'EFGH',
        'investigated_as': ['transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


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


def test_audit_antibody_lot_target(testapp, antibody_lot, base_antibody_characterization1, base_antibody_characterization2):
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'inconsistent target' for error in errors_list)


def test_audit_antibody_ar_dbxrefs(testapp, antibody_lot):
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing antibody registry reference' for error in errors_list)


def test_audit_control_characterizations(testapp, antibody_lot, base_target1):
    testapp.patch_json(base_target1['@id'], {'investigated_as': ['control']})
    testapp.patch_json(antibody_lot['@id'], {'targets': [base_target1['@id']]})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    errors = res.json['audit']
    print(errors)
    assert 'NOT_COMPLIANT' not in errors
