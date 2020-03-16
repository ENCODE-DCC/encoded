import pytest


def test_audit_none(testapp, biosample_type):
    res = testapp.get(biosample_type['@id'] + '@@index-data')
    assert res.json['audit'] == {}


def test_audit_ntr_biosample(testapp, ntr_biosample_type):
    res = testapp.get(ntr_biosample_type['@id'] + '@@index-data')
    errors = res.json['audit']
    assert len(errors) == len(errors['INTERNAL_ACTION']) == 1
    assert errors['INTERNAL_ACTION'][0]['category'] == 'NTR biosample'


def test_audit_not_in_ontology(testapp, id_nonexist_biosample_type):
    res = testapp.get(id_nonexist_biosample_type['@id'] + '@@index-data')
    errors = res.json['audit']
    assert len(errors) == len(errors['INTERNAL_ACTION']) == 1
    assert errors['INTERNAL_ACTION'][0]['category'] == 'term_id not in ontology'


def test_audit_inconsistent_type(testapp, inconsistent_biosample_type):
    res = testapp.get(inconsistent_biosample_type['@id'] + '@@index-data')
    errors = res.json['audit']
    assert len(errors) == len(errors['ERROR']) == 1
    assert errors['ERROR'][0]['category'] == 'inconsistent ontology term'
