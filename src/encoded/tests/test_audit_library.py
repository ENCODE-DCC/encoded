import pytest

@pytest.fixture
def library_no_biosample(testapp, lab, award):
    item = {
        'nucleic_acid_term_id': 'SO:0000352',
        'nucleic_acid_term_name': 'DNA',
        'lab': lab['@id'],
        'award': award['@id']
    }
    return testapp.post_json('/library', item).json['@graph'][0]


def test_audit_library_biosample(testapp, library_no_biosample):    
    res = testapp.get(library_no_biosample['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing biosample' for error in errors_list)
