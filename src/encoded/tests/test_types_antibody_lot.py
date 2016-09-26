import pytest


@pytest.fixture
def immunoblot(testapp, award, lab, antibody_lot, target, attachment):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'target': target['@id'],
        'characterizes': antibody_lot['@id'],
        'attachment': attachment,
        'primary_characterization_method': 'immunoblot',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def immunoprecipitation(immunoblot):
    item = immunoblot.copy()
    item.update({'primary_characterization': 'immunoprecipitation'})
    return item


@pytest.fixture
def mass_spec(testapp, award, lab, antibody_lot, target, attachment):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'target': target['@id'],
        'characterizes': antibody_lot['@id'],
        'attachment': attachment,
        'secondary_characterization_method': 'immunoprecipitation followed by mass spectrometry',
        'status': 'in progress'
    }
    return item


@pytest.fixture
def motif_enrichment(mass_spec):
    item = mass_spec.copy()
    item.update({'secondary_characterization_method': 'motif enrichment'})
    return item


# A single characterization (primary or secondary) associated with an ab that is not submitted
# for review, should result in a not pursued antibody lot status.
def test_not_submitted_primary_missing_secondary(testapp, immunoblot, antibody_lot):
    char = testapp.post_json('/AntibodyCharacterization', immunoblot).json['@graph'][0]
    testapp.patch_json(char['@id'], {'status': 'not submitted for review by lab'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not pursued'


# A single characterization (primary or secondary) associated with an ab that is not submitted
# for review, should result in a not pursued antibody lot status.
def test_not_submitted_secondary_missing_primary(testapp, motif_enrichment, antibody_lot):
    char = testapp.post_json('/AntibodyCharacterization', motif_enrichment).json['@graph'][0]
    testapp.patch_json(char['@id'], {'status': 'not submitted for review by lab'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not pursued'


def test_awaiting_in_progress_primary_missing_secondary(testapp, immunoblot, antibody_lot):
    testapp.post_json('/AntibodyCharacterization', immunoblot).json['@graph'][0]
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'


def test_awaiting_missing_secondary(testapp, immunoblot, antibody_lot, organism, target, 
                                    wrangler, document):
    char = testapp.post_json('/AntibodyCharacterization', immunoblot).json['@graph'][0]
    characterization_review = [{
        'biosample_term_name': 'K562',
        'biosample_term_id': 'EFO:0002067',
        'biosample_type': 'immortalized cell line',
        'organism': organism['@id'],
        'lane': 1,
        'lane_status': 'pending dcc review'
    }]
    testapp.patch_json(char['@id'], {
        'characterization_reviews': characterization_review,
        'status': 'pending dcc review'
    })
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    # Not yet reviewed primary and no secondary should result in ab status = pending dcc review
    assert ab['lot_reviews'][0]['detail'] == 'Pending review of primary and awaiting submission of secondary characterization(s).'
    assert ab['lot_reviews'][0]['status'] == 'pending dcc review'

    # Compliant primary and no secondary should result in ab status = awaiting characterization
    characterization_review[0]['lane_status'] = 'compliant'
    testapp.patch_json(char['@id'], {
        'characterization_reviews': characterization_review,
        'reviewed_by': wrangler['@id'],
        'documents': [document['@id']],
        'status': 'compliant'
    })
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting a compliant secondary characterization.'


# An in progress secondary and no primary should have ab status = awaiting characterization
def test_awaiting_missing_primary(testapp, mass_spec, motif_enrichment, antibody_lot, organism, target):
    char1 = testapp.post_json('/AntibodyCharacterization', mass_spec).json['@graph'][0]
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Characterizations in progress.'

    # Set the secondary for review and the ab status should be pending dcc review
    testapp.patch_json(char1['@id'], {'status': 'pending dcc review'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    # Change the code to make this pending dcc review instead of awaiting characterization?
    assert ab['lot_reviews'][0]['status'] == 'pending dcc review'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of primary characterization(s).'

    # A compliant secondary without primaries should have ab status = awaiting characterization
    testapp.patch_json(char1['@id'], {'status': 'compliant'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of primary characterization(s).'

    # Adding another secondary, regardless of status, should not change the ab status from awaiting
    char2 = testapp.post_json('/AntibodyCharacterization', motif_enrichment).json['@graph'][0]
    testapp.patch_json(char2['@id'], {'status': 'not compliant'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of primary characterization(s).'
