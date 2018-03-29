import pytest

@pytest.fixture
def gm_characterization(testapp, award, lab, construct_genetic_modification_N, attachment):
    item = {
        'characterizes': construct_genetic_modification_N['@id'],
        'award': award['@id'],
        'lab': lab['@id'],
        'attachment': attachment,
    }
    return testapp.post_json('/genetic_modification_characterization', item).json['@graph'][0]


def test_audit_tagging_gm_characterization(testapp,
                                           construct_genetic_modification_N,
                                           construct_genetic_modification,
                                           gm_characterization):

    res = testapp.get(construct_genetic_modification_N['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing genetic modification characterization' for error in errors_list)
    
    testapp.patch_json(gm_characterization['@id'], {'characterizes': construct_genetic_modification['@id']})
    res = testapp.get(construct_genetic_modification_N['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing genetic modification characterization' for error in errors_list)

