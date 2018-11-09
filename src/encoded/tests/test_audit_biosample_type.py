import pytest


@pytest.fixture
def base_biosample_type(testapp):
    item = {
        'term_ids': ['UBERON:349829',
                     'NTR:0000022',
                     'CL:99999999',
                     'EFO:0002067'],
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


def test_audit_biosample_type_term(testapp, base_biosample_type):
    res = testapp.get(base_biosample_type['@id'] + '@@index-data')
    errors = res.json['audit']
    assert 'INTERNAL_ACTION' in errors
    assert 'ERROR' in errors
    error_categories = set(e['category'] for e in errors['INTERNAL_ACTION'])
    assert error_categories == {'NTR biosample', 'term_id not in ontology'}
    assert errors['ERROR'][0]['category'] == 'inconsistent ontology term'
