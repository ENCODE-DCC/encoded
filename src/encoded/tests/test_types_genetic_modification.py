import pytest


def test_perturbation_flag(testapp, crispr_deletion_1, rnai_1, mpra_1, recomb_tag_1, crispr_tag_1):
    res = testapp.get(crispr_deletion_1['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == True
    res = testapp.get(rnai_1['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == True
    res = testapp.get(mpra_1['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == True
    res = testapp.get(recomb_tag_1['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == False
    res = testapp.get(crispr_tag_1['@id'] + '@@index-data')
    assert res.json['object']['perturbation'] == False