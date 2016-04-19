import pytest


def test_replaced_accession_not_in_name(testapp, human_donor):
    donor1 = human_donor
    assert donor1['accession'] in donor1['@id']
    donor1 = testapp.patch_json(
        donor1['@id'], {'status': 'replaced'}).json['@graph'][0]
    assert donor1['accession'] not in donor1['@id']


def test_accession_replacement(testapp, human_donor):
    donor1 = human_donor
    donor1 = testapp.patch_json(
        donor1['@id'], {'status': 'replaced'}).json['@graph'][0]

    donor2 = human_donor
    donor2 = testapp.patch_json(
        donor1['@id'], {'alternate_accessions': [donor1['accession']]}).json['@graph'][0]

    res = testapp.get('/' + donor1['accession']).maybe_follow()
    assert res.json['@id'] == donor2['@id']
