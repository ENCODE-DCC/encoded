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
    item.update({'primary_characterization_method': 'immunoprecipitation'})
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


@pytest.fixture
def mouse_target(testapp, mouse):
    item = {
        'label': 'ATF4',
        'organism': mouse['@id'],
        'investigated_as': ['transcription factor'],
    }
    return testapp.post_json('/target', item).json['@graph'][0]


@pytest.fixture
def mouse_target_H3K9me3(testapp, mouse):
    item = {
        'label': 'H3K9me3',
        'organism': mouse['@id'],
        'investigated_as': ['histone modification',
                            'histone',
                            'broad histone mark']
    }
    return testapp.post_json('/target', item).json['@graph'][0]


# A single characterization (primary or secondary) associated with an ab that is not submitted
# for review, should result in a not pursued antibody lot status.
def test_not_submitted_primary_missing_secondary(testapp, immunoblot, antibody_lot):
    char = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    testapp.patch_json(char['@id'], {'status': 'not submitted for review by lab'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    print("{}".format(ab['characterizations']))
    print("{}".format(ab['lot_reviews']))
    assert ab['lot_reviews'][0]['status'] == 'not pursued'


# A single characterization (primary or secondary) associated with an ab that is not submitted
# for review, should result in a not pursued antibody lot status.
def test_not_submitted_secondary_missing_primary(testapp, motif_enrichment, antibody_lot):
    char = testapp.post_json('/antibody_characterization', motif_enrichment).json['@graph'][0]
    testapp.patch_json(char['@id'], {'status': 'not submitted for review by lab'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not pursued'


def test_awaiting_in_progress_primary_missing_secondary(testapp, immunoblot, antibody_lot):
    testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'


def test_have_primary_missing_secondary(testapp,
                                        immunoblot,
                                        antibody_lot,
                                        human,
                                        target,
                                        wrangler,
                                        document):
    char = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    characterization_review = {
        'biosample_term_name': 'K562',
        'biosample_term_id': 'EFO:0002067',
        'biosample_type': 'immortalized cell line',
        'organism': human['@id'],
        'lane': 1
    }

    # An in progress primary and no secondary should result in awaiting characterization
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Primary characterization(s) in progress.'

    # Not yet reviewed primary and no secondary should result in ab status = pending dcc review
    characterization_review['lane_status'] = 'pending dcc review'
    testapp.put_json(char['@id'], immunoblot).json['@graph'][0]
    testapp.patch_json(char['@id'], {
        'characterization_reviews': [characterization_review],
        'status': 'pending dcc review'
    })
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'pending dcc review'
    assert ab['lot_reviews'][0]['detail'] == 'One or more characterization(s) is pending review.'

    # No secondary and a primary that is not submitted for review should result in
    # ab status = not pursued
    testapp.put_json(char['@id'], immunoblot).json['@graph'][0]
    testapp.patch_json(char['@id'], {'status': 'not submitted for review by lab'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not pursued'
    assert ab['lot_reviews'][0]['detail'] is None

    '''
    # Compliant primary and no secondary should result in ab status = not characterized to standards
    characterization_review['lane_status'] = 'compliant'

    testapp.patch_json(char['@id'], {
        'status': 'compliant',
        'characterization_reviews': [characterization_review],
        'reviewed_by': wrangler['@id'],
        'documents': [document['@id']]
    })

    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not characterized to standards'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of secondary characterization(s).'
    '''

# An in progress secondary and no primary should have ab status = awaiting characterization
def test_have_secondary_missing_primary(testapp,
                                        mass_spec,
                                        motif_enrichment,
                                        antibody_lot,
                                        human,
                                        target,
                                        wrangler,
                                        document):
    # in progress secondary and no primary = awaiting characterization
    char1 = testapp.post_json('/antibody_characterization', mass_spec).json['@graph'][0]
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of primary characterization(s).'

    # Set the secondary for review and the ab status should be pending dcc review
    testapp.patch_json(char1['@id'], {'status': 'pending dcc review'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'pending dcc review'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of primary characterization(s).'

    # A compliant secondary without primaries should be not characterized to standards as per Cricket's
    # wishes
    testapp.patch_json(char1['@id'], {'status': 'compliant',
                                      'reviewed_by': wrangler['@id'],
                                      'documents': [document['@id']]})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not characterized to standards'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of primary characterization(s).'

    # Adding another secondary, regardless of status, should not change the ab status from
    # not characterized to standards
    char2 = testapp.post_json('/antibody_characterization', motif_enrichment).json['@graph'][0]
    testapp.patch_json(char2['@id'], {'status': 'not compliant',
                                      'reviewed_by': wrangler['@id'],
                                      'documents': [document['@id']]})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not characterized to standards'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of primary characterization(s).'


# If there are multiple secondary characterizations, the one with the highest status ranking should
# prevail
def test_multiple_secondary_one_primary(testapp,
                                        mass_spec,
                                        motif_enrichment,
                                        immunoblot,
                                        antibody_lot,
                                        human,
                                        target,
                                        wrangler,
                                        document):

    prim_char = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    sec_char1 = testapp.post_json('/antibody_characterization', motif_enrichment).json['@graph'][0]
    sec_char2 = testapp.post_json('/antibody_characterization', mass_spec).json['@graph'][0]
    characterization_review = {
        'biosample_term_name': 'K562',
        'biosample_term_id': 'EFO:0002067',
        'biosample_type': 'immortalized cell line',
        'organism': human['@id'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    testapp.patch_json(prim_char['@id'], {'status': 'compliant',
                                          'reviewed_by': wrangler['@id'],
                                          'documents': [document['@id']],
                                          'characterization_reviews': [characterization_review]})
    testapp.patch_json(sec_char1['@id'], {'status': 'not compliant',
                                          'reviewed_by': wrangler['@id'],
                                          'documents': [document['@id']]})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not characterized to standards'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting a compliant secondary characterization.'

    # Add another secondary characterization with exempted status and it should override the
    # not compliant of the motif enrichment characterization
    testapp.patch_json(sec_char2['@id'], {'status': 'exempt from standards',
                                          'reviewed_by': wrangler['@id'],
                                          'documents': [document['@id']],
                                          'comment': 'Required plea for exemption',
                                          'notes': 'Required reviewer note'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'characterized to standards with exemption'
    assert ab['lot_reviews'][0]['detail'] == 'Fully characterized with exemption.'

    # Making the not compliant motif enrichment characterization now compliant should
    # override the exempt from standards mass spec
    testapp.patch_json(sec_char1['@id'], {'status': 'compliant'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'characterized to standards'
    assert ab['lot_reviews'][0]['detail'] == 'Fully characterized.'


# An antibody against histone modifications with primaries in human (compliant) and mouse
# (not compliant) and an exempt secondary should yield exemption in human and not
# charaterized to standards in mouse
def test_histone_mod_characterizations(testapp,
                                       immunoblot,
                                       immunoprecipitation,
                                       mass_spec,
                                       antibody_lot,
                                       human,
                                       mouse,
                                       target_H3K9me3,
                                       mouse_target_H3K9me3,
                                       wrangler,
                                       document):

    prim_char_human = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    prim_char_mouse = testapp.post_json('/antibody_characterization', immunoprecipitation).json['@graph'][0]
    sec_char = testapp.post_json('/antibody_characterization', mass_spec).json['@graph'][0]
    testapp.patch_json(antibody_lot['@id'], {'targets': [target_H3K9me3['@id'], mouse_target_H3K9me3['@id']]})
    characterization_review_human = {
        'biosample_term_name': 'K562',
        'biosample_term_id': 'EFO:0002067',
        'biosample_type': 'immortalized cell line',
        'organism': human['@id'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    characterization_review_mouse = {
        'biosample_term_name': 'CH12.LX',
        'biosample_term_id': 'EFO:0005233',
        'biosample_type': 'immortalized cell line',
        'organism': mouse['@id'],
        'lane': 1,
        'lane_status': 'not compliant'
    }
    testapp.patch_json(prim_char_human['@id'], {'status': 'compliant',
                                                'reviewed_by': wrangler['@id'],
                                                'documents': [document['@id']],
                                                'target': target_H3K9me3['@id'],
                                                'characterization_reviews': [
                                                    characterization_review_human]})
    testapp.patch_json(prim_char_mouse['@id'], {'status': 'not compliant',
                                                'reviewed_by': wrangler['@id'],
                                                'documents': [document['@id']],
                                                'target': mouse_target_H3K9me3['@id'],
                                                'characterization_reviews': [
                                                    characterization_review_mouse]})
    testapp.patch_json(sec_char['@id'], {'status': 'exempt from standards',
                                         'comment': 'Please exempt this.',
                                         'notes': 'OK.',
                                         'reviewed_by': wrangler['@id'],
                                         'documents': [document['@id']],
                                         'target': target_H3K9me3['@id']})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert len(ab['lot_reviews']) == 2
    for review in ab['lot_reviews']:
        if human['@id'] in review['organisms']:
            assert review['status'] == 'characterized to standards with exemption'
            assert review['detail'] == 'Fully characterized with exemption.'

        if mouse['@id'] in review['organisms']:
            assert review['status'] == 'not characterized to standards'
            assert review['detail'] == 'Awaiting a compliant primary characterization.'
    '''
    Adding another primary in mouse that is exempt from standards should make mouse now exempt
    '''
    prim_char_mouse2 = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    characterization_review_mouse['lane_status'] = 'not compliant'
    characterization_review_mouse2 = characterization_review_mouse.copy()
    characterization_review_mouse2.update({'biosample_term_name': 'erythroblast',
                                           'biosample_term_id': 'CL:0000765',
                                           'biosample_type': 'primary cell',
                                           'lane_status': 'exempt from standards',
                                           'lane': 2})

    testapp.patch_json(prim_char_mouse2['@id'], {'status': 'exempt from standards',
                                                 'reviewed_by': wrangler['@id'],
                                                 'comment': 'Please exempt this.',
                                                 'notes': 'OK',
                                                 'documents': [document['@id']],
                                                 'target': mouse_target_H3K9me3['@id'],
                                                 'characterization_reviews': [
                                                     characterization_review_mouse,
                                                     characterization_review_mouse2]})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert len(ab['lot_reviews']) == 2
    for review in ab['lot_reviews']:
        assert review['status'] == 'characterized to standards with exemption'
        assert review['detail'] == 'Fully characterized with exemption.'


# A test for multiple lanes to make sure all of the statuses for each cell type and tissue
# are calculated properly.
def test_multi_lane_primary(testapp,
                            immunoblot,
                            immunoprecipitation,
                            mass_spec,
                            antibody_lot,
                            human,
                            mouse,
                            target,
                            mouse_target,
                            wrangler,
                            document):

    prim_char = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    sec_char = testapp.post_json('/antibody_characterization', mass_spec).json['@graph'][0]
    testapp.patch_json(antibody_lot['@id'], {'targets': [target['@id'], mouse_target['@id']]})
    characterization_review = {
        'biosample_term_name': 'K562',
        'biosample_term_id': 'EFO:0002067',
        'biosample_type': 'immortalized cell line',
        'organism': human['@id'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    characterization_review_2 = characterization_review.copy()
    characterization_review_2.update({'biosample_term_name': 'HepG2',
                                      'biosample_term_id': 'EFO:0001187',
                                      'lane': 2,
                                      'lane_status': 'not compliant'})
    characterization_review_3 = characterization_review.copy()
    characterization_review_3.update({'biosample_term_name': 'GM12878',
                                      'biosample_term_id': 'EFO:0002784',
                                      'lane': 3,
                                      'lane_status': 'exempt from standards'})
    testapp.patch_json(prim_char['@id'], {'status': 'compliant',
                                          'reviewed_by': wrangler['@id'],
                                          'documents': [document['@id']],
                                          'comment': 'Please exempt this.',
                                          'notes': 'OK.',
                                          'target': target['@id'],
                                          'characterization_reviews': [characterization_review,
                                                                       characterization_review_2,
                                                                       characterization_review_3]})
    testapp.patch_json(sec_char['@id'], {'status': 'compliant',
                                         'reviewed_by': wrangler['@id'],
                                         'documents': [document['@id']],
                                         'target': target['@id']})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert len(ab['lot_reviews']) == 3
    for review in ab['lot_reviews']:
        if review['biosample_term_name'] == 'K562':
            assert review['status'] == 'characterized to standards'
            assert review['detail'] == 'Fully characterized.'
        if review['biosample_term_name'] == 'GM12878':
            assert review['status'] == 'characterized to standards with exemption'
            assert review['detail'] == 'Fully characterized with exemption.'
        if review['biosample_term_name'] == 'HepG2':
            assert review['status'] == 'not characterized to standards'
            assert review['detail'] == 'Awaiting a compliant primary characterization.'

    # Now, if we change the secondary to be not reviewed, all statuses will be not characterized to
    # standard since we absolutely need a compliant or exempted secondary to be characterized to
    # standards.
    testapp.patch_json(sec_char['@id'], {'status': 'not reviewed'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert len(ab['lot_reviews']) == 3
    for review in ab['lot_reviews']:
            assert review['status'] == 'not characterized to standards'
            assert review['detail'] == 'Awaiting a compliant secondary characterization.'
