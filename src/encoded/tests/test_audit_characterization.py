import pytest


def test_audit_biosample_characterization_review_lane_not_required(
        testapp,
        biosample_characterization,
        review,
):
    testapp.patch_json(
        biosample_characterization['@id'],
        {
            'review': review,
            'characterization_method': 'immunoprecipitation followed by mass spectrometry',
        }
    )
    res = testapp.get(biosample_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert not any(error['category'] == 'missing review lane' for error in errors_list)


def test_audit_biosample_characterization_review_lane_required(
        testapp,
        biosample_characterization,
        review,
):
    testapp.patch_json(
        biosample_characterization['@id'],
        {
            'review': review,
            'characterization_method': 'immunoblot',
        }
    )
    res = testapp.get(biosample_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing review lane' for error in errors_list)


def test_audit_genetic_modification_characterization_review_lane_not_required(
        testapp,
        gm_characterization,
        review,
):
    testapp.patch_json(
        gm_characterization['@id'],
        {
            'review': review,
            'characterization_method': 'Sanger sequencing',
        }
    )
    res = testapp.get(gm_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert not any(error['category'] == 'missing review lane' for error in errors_list)


def test_audit_genetic_modification_characterization_review_lane_required(
        testapp,
        gm_characterization,
        review,
):
    testapp.patch_json(
        gm_characterization['@id'],
        {
            'review': review,
            'characterization_method': 'immunoblot',
        }
    )
    res = testapp.get(gm_characterization['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing review lane' for error in errors_list)
