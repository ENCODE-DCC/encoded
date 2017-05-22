import pytest


@pytest.fixture
def human_donor(lab, award, organism):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'organism': organism['uuid'],
    }


def test_replaced_accession_not_in_name(testapp, human_donor):
    donor1 = testapp.post_json('/human_donor', human_donor, status=201).json['@graph'][0]
    assert donor1['accession'] in donor1['@id']
    donor1 = testapp.patch_json(
        donor1['@id'], {'status': 'replaced'}).json['@graph'][0]
    assert donor1['accession'] not in donor1['@id']


def test_accession_replacement(testapp, human_donor):
    donor1 = testapp.post_json('/human_donor', human_donor, status=201).json['@graph'][0]
    donor1 = testapp.patch_json(
        donor1['@id'], {'status': 'replaced'}).json['@graph'][0]

    donor2 = testapp.post_json('/human_donor', human_donor, status=201).json['@graph'][0]
    donor2 = testapp.patch_json(
        donor2['@id'], {'alternate_accessions': [donor1['accession']]}).json['@graph'][0]

    res = testapp.get('/' + donor1['accession']).maybe_follow()
    assert res.json['@id'] == donor2['@id']


def test_admin_put_accession(human_donor, testapp):
    url = '/human_donor'
    # but coudl be any accessoned object
    donor1 = testapp.post_json(url, human_donor, status=201).json['@graph'][0]

    donor1.update({'accession': 'ENCDO111BBB'})
    # initial test
    testapp.put_json(donor1['@id'], donor1, status=200)
    res = testapp.get(url)
    assert(res.json['accession'] == "ENCDO111BBB")

    donor1.update({'accession': 'somerstring'})
    testapp.put_json(donor1['@id'], donor1, status=200)
