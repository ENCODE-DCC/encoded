import pytest


@pytest.fixture
def base_biosample(testapp, source, award, lab, organism):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'source': source['uuid'],
        'organism': organism['uuid']
    }
    return testapp.post_json('biosample', item, status=201).json['@graph'][0]


@pytest.fixture
def base_human(testapp, name, taxon_id, scientific_name):
    item = {
        'name': 'human',
        'taxon_id': '9606',
        'scientific_name': 'Homo sapiens'
    }
    return testapp.post_json('organism', item, status=201).json['@graph'][0]

@pytest.fixture
def base_fly(testapp, name, taxon_id, scientific_name):
    item = {
        'name': 'dmelanogaster',
        'taxon_id': '7227',
        'scientific_name': 'Drosophila melanogaster'
    }
    return testapp.post_json('organism', item, status=201).json['@graph'][0]


@pytest.fixture
def base_human_donor(testapp, award, lab, base_human):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid']
        'organism': base_human['@id']
    }
    return testapp.post_json('human-donors', item, status=201).json['@graph'][0]


@pytest.fixture
def base_fly_donor(testapp, award, lab, base_fly):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid']
        'organism': base_fly['@id']
    }
    return testapp.post_json('fly-donors', item, status=201).json['@graph'][0]


def test_audit_biosample_term_ntr(testapp, ntr_biosample):
    res = testapp.patch_json(base_biosample['@id'], {'biosample_term_id': 'NTR:0000022', 'biosample_term_name': 'myocyte', 'biosample_type': 'in vitro differentiated cells'})
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'NTR'


def test_audit_biosample_culture_dates(testapp, base_biosample):
    res = testapp.patch_json(base_biosample['@id'], {'culture_start_date': '2014-06-30', 'culture_harvest_date': '2014-06-25'})
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'invalid dates'


def test_audit_biosample_donor(testapp, base_biosample):
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'missing donor'


def test_audit_biosample_donor_organism(testapp, base_biosample, base_human_donor, base_fly):
    res = testapp.patch_json(base_biosample['@id'], {'donor': base_human_donor['@id'], 'organism': base_fly['@id']})
    res = testapp.get(res.location + '@@index-data')
    error, = res.json['audit']
    assert error['category'] == 'organism mismatch'
    