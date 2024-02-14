import pytest
from .constants import RED_DOT


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
