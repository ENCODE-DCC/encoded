import pytest


@pytest.fixture
def ntr_biosample_type(testapp):
    item = {
        'term_id': 'NTR:0000022',
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def id_nonexist_biosample_type(testapp):
    item = {
        'term_id': 'CL:99999999',
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


@pytest.fixture
def inconsistent_biosample_type(testapp):
    item = {
        'term_id': 'EFO:0002067',
        'term_name': 'heart',
        'classification': 'single cell',
    }
    return testapp.post_json('/biosample-types', item, status=201).json['@graph'][0]


def test_audit_biosample_type_term(testapp,
                                   ntr_biosample_type,
                                   id_nonexist_biosample_type,
                                   inconsistent_biosample_type):
    res = testapp.get(ntr_biosample_type['@id'] + '@@index-data')
    errors = res.json['audit']
    assert len(errors) == len(errors['INTERNAL_ACTION']) == 1
    assert errors['INTERNAL_ACTION'][0]['category'] == 'NTR biosample'

    res = testapp.get(id_nonexist_biosample_type['@id'] + '@@index-data')
    errors = res.json['audit']
    assert len(errors) == len(errors['INTERNAL_ACTION']) == 1
    assert errors['INTERNAL_ACTION'][0]['category'] == 'term_id not in ontology'

    res = testapp.get(inconsistent_biosample_type['@id'] + '@@index-data')
    errors = res.json['audit']
    assert len(errors) == len(errors['ERROR']) == 1
    assert errors['ERROR'][0]['category'] == 'inconsistent ontology term'
