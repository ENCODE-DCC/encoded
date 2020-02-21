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


@pytest.fixture
def gfp_target(testapp, organism):
    item = {
        'label': 'gfp',
        'target_organism': organism['@id'],
        'investigated_as': ['tag'],
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def encode4_tag_antibody_lot(testapp, lab, encode4_award, source, mouse, gfp_target):
    item = {
        'product_id': 'WH0000468M1',
        'lot_id': 'CB191-2B3',
        'award': encode4_award['@id'],
        'lab': lab['@id'],
        'source': source['@id'],
        'host_organism': mouse['@id'],
        'targets': [gfp_target['@id']],
    }
    return testapp.post_json('/antibody_lot', item).json['@graph'][0]


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


def test_audit_control_characterizations(testapp, control_antibody):
    res = testapp.get(control_antibody['@id'] + '@@index-data')
    errors = res.json['audit']
    print(errors)
    assert 'NOT_COMPLIANT' not in errors


def test_audit_encode4_tag_ab_characterizations(
    testapp,
    encode4_tag_antibody_lot,
    biosample_characterization,
    lab,
    submitter
):
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    errors = res.json['audit']
    assert any(
        error['category'] == 'no characterizations submitted'
        for errs in errors.values() for error in errs
    )
    testapp.patch_json(
        biosample_characterization['@id'],
        {'antibody': encode4_tag_antibody_lot['@id']}
    )
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    errors = res.json['audit']
    assert all(
        error['category'] != 'no characterizations submitted'
        for errs in errors.values() for error in errs
    )
    assert any(
        error['category'] == 'need one compliant biosample characterization'
        for errs in errors.values() for error in errs
    )
    testapp.patch_json(
        biosample_characterization['@id'],
        {
            'review': {
                'lab': lab['@id'],
                'reviewed_by': submitter['@id'],
                'status': 'exempt from standards'
            }
        }
    )
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    errors = res.json['audit']
    assert all(
        error['category'] != 'no characterizations submitted'
        for errs in errors.values() for error in errs
    )
    assert all(
        error['category'] != 'need one compliant biosample characterization'
        for errs in errors.values() for error in errs
    )


def test_audit_encode3_tag_ab_characterizations(
    testapp,
    antibody_lot,
    gfp_target,
    biosample_characterization,
    base_antibody_characterization1,
    lab,
    submitter
):
    testapp.patch_json(antibody_lot['@id'], {'targets': [gfp_target['@id']]})
    biosample = testapp.get(biosample_characterization['characterizes']).json
    testapp.patch_json(
        base_antibody_characterization1['@id'],
        {
            'target': gfp_target['uuid'],
            'characterization_reviews': [{
                'lane': 1,
                'organism': biosample['organism']['uuid'],
                'biosample_ontology': biosample['biosample_ontology']['uuid'],
                'lane_status': 'not compliant'
            }]
        }
    )
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    errors = [err for errs in res.json['audit'].values() for err in errs]
    assert any(error['category'] == 'need compliant primaries' for error in errors)
    assert any(error['category'] == 'no secondary characterizations' for error in errors)
    testapp.patch_json(
        biosample_characterization['@id'],
        {
            'review': {
                'status': 'compliant',
                'lab': lab['@id'],
                'reviewed_by': submitter['@id'],
            },
            'antibody': antibody_lot['@id']
        }
    )
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    errors = [err for errs in res.json['audit'].values() for err in errs]
    assert all(error['category'] != 'need compliant primaries' for error in errors)
    assert all(error['category'] != 'no secondary characterizations' for error in errors)
