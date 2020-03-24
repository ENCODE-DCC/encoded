import pytest


# A single characterization (primary or secondary) associated with an ab that is not submitted
# for review, should result in a not pursued antibody lot status.
def test_not_submitted_secondary_missing_primary(testapp, motif_enrichment, antibody_lot):
    char = testapp.post_json('/antibody_characterization', motif_enrichment).json['@graph'][0]
    testapp.patch_json(char['@id'], {'status': 'not submitted for review by lab'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not pursued'


def test_have_primary_missing_secondary(testapp,
                                        immunoblot,
                                        antibody_lot,
                                        human,
                                        target,
                                        wrangler,
                                        document,
                                        k562):
    char = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    characterization_review = {
        'biosample_ontology': k562['uuid'],
        'organism': human['@id'],
        'lane': 1
    }

    # An in progress primary and no secondary should result in awaiting characterization
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting a compliant primary and submission of a secondary characterization.'

    # Not yet reviewed primary and no secondary should result in ab status = awaiting characterization
    characterization_review['lane_status'] = 'pending dcc review'
    testapp.put_json(char['@id'], immunoblot).json['@graph'][0]
    testapp.patch_json(char['@id'], {
        'characterization_reviews': [characterization_review],
        'status': 'pending dcc review'
    })
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Pending review of primary characterization and ' + \
        'awaiting submission of a secondary characterization.'

    # No secondary and a primary that is not submitted for review should result in
    # ab status = not pursued
    testapp.put_json(char['@id'], immunoblot).json['@graph'][0]
    testapp.patch_json(char['@id'], {'status': 'not submitted for review by lab'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not pursued'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting a compliant primary and submission of a secondary characterization.'

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
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of a primary characterization ' + \
        'and a compliant secondary characterization.'

    # Set the secondary for review and the ab status should be awaiting characterization
    testapp.patch_json(char1['@id'], {'status': 'pending dcc review'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of a primary characterization ' + \
        'and pending review of a secondary characterization.'

    # A compliant secondary without primaries is partially characterized
    testapp.patch_json(char1['@id'], {'status': 'compliant',
                                      'reviewed_by': wrangler['@id'],
                                      'documents': [document['@id']]})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'partially characterized'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of a primary characterization.'

    # Adding another secondary, regardless of status, should not change the ab status from
    # partially characterized.
    char2 = testapp.post_json('/antibody_characterization', motif_enrichment).json['@graph'][0]
    testapp.patch_json(char2['@id'], {'status': 'not compliant',
                                      'reviewed_by': wrangler['@id'],
                                      'documents': [document['@id']]})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'partially characterized'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting submission of a primary characterization.'


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
                                        document,
                                        k562):

    prim_char = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    sec_char1 = testapp.post_json('/antibody_characterization', motif_enrichment).json['@graph'][0]
    sec_char2 = testapp.post_json('/antibody_characterization', mass_spec).json['@graph'][0]
    characterization_review = {
        'biosample_ontology': k562['uuid'],
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
                                          'submitter_comment': 'Required plea for exemption',
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
                                       document,
                                       liver,
                                       erythroblast):

    prim_char_human = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    prim_char_mouse = testapp.post_json('/antibody_characterization', immunoprecipitation).json['@graph'][0]
    sec_char = testapp.post_json('/antibody_characterization', mass_spec).json['@graph'][0]
    testapp.patch_json(antibody_lot['@id'], {'targets': [target_H3K9me3['@id'], mouse_target_H3K9me3['@id']]})
    characterization_review_human = {
        'biosample_ontology': liver['uuid'],
        'organism': human['@id'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    characterization_review_mouse = {
        'biosample_ontology': liver['uuid'],
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
                                         'submitter_comment': 'Please exempt this.',
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

    # Adding another primary in mouse that is exempt from standards should make mouse now exempt
    prim_char_mouse2 = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    characterization_review_mouse['lane_status'] = 'not compliant'
    characterization_review_mouse2 = characterization_review_mouse.copy()
    characterization_review_mouse2.update({'biosample_ontology': erythroblast['uuid'],
                                           'lane_status': 'exempt from standards',
                                           'lane': 2})

    testapp.patch_json(prim_char_mouse2['@id'], {'status': 'exempt from standards',
                                                 'reviewed_by': wrangler['@id'],
                                                 'submitter_comment': 'Please exempt this.',
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
                            document,
                            k562,
                            hepg2,
                            gm12878):

    prim_char = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    sec_char = testapp.post_json('/antibody_characterization', mass_spec).json['@graph'][0]
    testapp.patch_json(antibody_lot['@id'], {'targets': [target['@id'], mouse_target['@id']]})
    characterization_review = {
        'biosample_ontology': k562['uuid'],
        'organism': human['@id'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    characterization_review_2 = {'biosample_ontology': hepg2['uuid'],
                                 'organism': human['@id'],
                                 'lane': 2,
                                 'lane_status': 'not compliant'}

    characterization_review_3 = {'biosample_ontology': gm12878['uuid'],
                                 'organism': human['@id'],
                                 'lane': 3,
                                 'lane_status': 'exempt from standards'}
    testapp.patch_json(prim_char['@id'], {'status': 'compliant',
                                          'reviewed_by': wrangler['@id'],
                                          'documents': [document['@id']],
                                          'submitter_comment': 'Please exempt this.',
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

    # Now, if we change the secondary to be not reviewed, the antibody should now only be
    # partially characterized on the strength of the compliant and exempt primaries. The
    # not compliant primary should now be not characterized to standards.
    testapp.patch_json(sec_char['@id'], {'status': 'not reviewed'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert len(ab['lot_reviews']) == 3
    for review in ab['lot_reviews']:
        if review['biosample_term_name'] in ['K562', 'GM12878']:
            assert review['status'] == 'partially characterized'
        if review['biosample_term_name'] == 'HepG2':
            assert review['status'] == 'not characterized to standards'
            assert review['detail'] == 'Awaiting a compliant primary and secondary characterization not reviewed.'


# Status calculation test for when primaries have extraneous characterization_reviews
def test_bonus_char_reviews_in_primary(testapp,
                                       immunoblot,
                                       immunoprecipitation,
                                       mass_spec,
                                       antibody_lot,
                                       human,
                                       target,
                                       wrangler,
                                       document,
                                       k562,
                                       hepg2):

    # A not submitted for review primary with no secondary should give status of not pursued
    prim_char1 = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    characterization_review1 = {
        'biosample_ontology': k562['uuid'],
        'organism': human['@id'],
        'lane': 1,
        'lane_status': 'pending dcc review'
    }
    testapp.patch_json(prim_char1['@id'], {'status': 'not submitted for review by lab',
                                           'target': target['@id'],
                                           'characterization_reviews': [characterization_review1]})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'not pursued'
    assert ab['lot_reviews'][0]['detail'] == 'Awaiting a compliant primary and submission of a secondary characterization.'

    # Adding an in progress primary in a different cell type should result in the ab awaiting characterization
    prim_char2 = testapp.post_json('/antibody_characterization', immunoprecipitation).json['@graph'][0]
    characterization_review2 = {
        'biosample_ontology': hepg2['uuid'],
        'organism': human['@id'],
        'lane': 1,
        'lane_status': 'pending dcc review'
    }
    testapp.patch_json(prim_char2['@id'], {'status': 'in progress',
                                           'target': target['@id'],
                                           'characterization_reviews': [characterization_review2]})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert len(ab['lot_reviews']) == 2
    for review in ab['lot_reviews']:
        if review['biosample_term_name'] == 'K562':
            assert review['status'] == 'not pursued'
        if review['biosample_term_name'] == 'HepG2':
            assert review['status'] == 'awaiting characterization'
            assert review['detail'] == 'Awaiting a compliant primary and submission of a secondary characterization.'

    # Adding an exempted secondary should make the ab partially characterized
    sec_char = testapp.post_json('/antibody_characterization', mass_spec).json['@graph'][0]
    testapp.patch_json(sec_char['@id'], {'status': 'exempt from standards',
                                         'target': target['@id'],
                                         'reviewed_by': wrangler['@id'],
                                         'documents': [document['@id']],
                                         'submitter_comment': 'Please exempt this.',
                                         'notes': 'OK.'})
    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert len(ab['lot_reviews']) == 2
    for review in ab['lot_reviews']:
        if review['biosample_term_name'] in ['K562', 'HepG2']:
            assert review['status'] == 'partially characterized'
            assert review['detail'] == 'Awaiting a compliant primary characterization.'


# Status calculation test for when primary and secondary characterizations are both not reviewed
def test_chars_not_reviewed(testapp,
                            immunoblot,
                            mass_spec,
                            antibody_lot,
                            target,
                            wrangler):

    prim_char = testapp.post_json('/antibody_characterization', immunoblot).json['@graph'][0]
    testapp.patch_json(prim_char['@id'], {'status': 'not reviewed',
                                          'reviewed_by': wrangler['@id'],
                                          'target': target['@id']})

    sec_char = testapp.post_json('/antibody_characterization', mass_spec).json['@graph'][0]
    testapp.patch_json(sec_char['@id'], {'status': 'not reviewed',
                                         'reviewed_by': wrangler['@id'],
                                         'target': target['@id']})

    res = testapp.get(antibody_lot['@id'] + '@@index-data')
    ab = res.json['object']
    assert ab['lot_reviews'][0]['status'] == 'awaiting characterization'
    assert ab['lot_reviews'][0]['detail'] == 'Primary and secondary characterizations not reviewed.'


def test_encode4_tagged_ab_review_status(testapp,
                                         encode4_tag_antibody_lot,
                                         biosample_characterization_no_review,
                                         biosample_characterization_2nd_opinion,
                                         biosample_characterization_exempt,
                                         biosample_characterization_not_compliant,
                                         biosample_characterization_compliant,
                                         biosample_2_liver):
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    assert len(res.json['object']['used_by_biosample_characterizations']) == 0
    assert res.json['object']['lot_reviews'] == [{
        'biosample_term_id': 'NTR:99999999',
        'biosample_term_name': 'any cell type or tissue',
        'detail': 'Awaiting to be linked to biosample characterizations.',
        'organisms': ['/organisms/human/'],
        'status': 'awaiting characterization',
        'targets': ['/targets/gfp-human/'],
    }]
    testapp.patch_json(biosample_characterization_not_compliant['@id'],
                       {'antibody': encode4_tag_antibody_lot['@id']})
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    assert len(res.json['object']['used_by_biosample_characterizations']) == 1
    assert res.json['object']['lot_reviews'] == [{
        'biosample_term_id': 'UBERON:0000948',
        'biosample_term_name': 'heart',
        'detail': 'Awaiting compliant biosample characterizations.',
        'organisms': ['/organisms/human/'],
        'status': 'not characterized to standards',
        'targets': ['/targets/gfp-human/'],
    }]
    testapp.patch_json(biosample_characterization_no_review['@id'],
                       {'antibody': encode4_tag_antibody_lot['@id']})
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    assert len(res.json['object']['used_by_biosample_characterizations']) == 2
    assert res.json['object']['lot_reviews'] == [{
        'biosample_term_id': 'UBERON:0000948',
        'biosample_term_name': 'heart',
        'detail': 'Awaiting to be linked to biosample characterizations.',
        'organisms': ['/organisms/human/'],
        'status': 'awaiting characterization',
        'targets': ['/targets/gfp-human/'],
    }]
    testapp.patch_json(biosample_characterization_2nd_opinion['@id'],
                       {'antibody': encode4_tag_antibody_lot['@id']})
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    assert len(res.json['object']['used_by_biosample_characterizations']) == 3
    assert res.json['object']['lot_reviews'] == [{
        'biosample_term_id': 'UBERON:0000948',
        'biosample_term_name': 'heart',
        'detail': 'Awaiting to be linked to biosample characterizations.',
        'organisms': ['/organisms/human/'],
        'status': 'awaiting characterization',
        'targets': ['/targets/gfp-human/'],
    }]
    testapp.patch_json(biosample_characterization_exempt['@id'],
                       {'antibody': encode4_tag_antibody_lot['@id']})
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    assert len(res.json['object']['used_by_biosample_characterizations']) == 4
    assert res.json['object']['lot_reviews'] == [{
        'biosample_term_id': 'UBERON:0000948',
        'biosample_term_name': 'heart',
        'detail': 'Fully characterized with exemption.',
        'organisms': ['/organisms/human/'],
        'status': 'characterized to standards with exemption',
        'targets': ['/targets/gfp-human/'],
    }]
    testapp.patch_json(biosample_characterization_compliant['@id'],
                       {'antibody': encode4_tag_antibody_lot['@id']})
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    assert len(res.json['object']['used_by_biosample_characterizations']) == 5
    assert res.json['object']['lot_reviews'] == [{
        'biosample_term_id': 'UBERON:0000948',
        'biosample_term_name': 'heart',
        'detail': 'Fully characterized.',
        'organisms': ['/organisms/human/'],
        'status': 'characterized to standards',
        'targets': ['/targets/gfp-human/'],
    }]
    testapp.patch_json(biosample_characterization_exempt['@id'],
                       {'characterizes': biosample_2_liver['@id']})
    res = testapp.get(encode4_tag_antibody_lot['@id'] + '@@index-data')
    assert len(res.json['object']['used_by_biosample_characterizations']) == 5
    assert len(res.json['object']['lot_reviews']) == 2
    assert {
        'biosample_term_id': 'UBERON:0000948',
        'biosample_term_name': 'heart',
        'detail': 'Fully characterized.',
        'organisms': ['/organisms/human/'],
        'status': 'characterized to standards',
        'targets': ['/targets/gfp-human/'],
    } in res.json['object']['lot_reviews']
    assert {
        'biosample_term_id': 'UBERON:0002107',
        'biosample_term_name': 'liver',
        'detail': 'Fully characterized with exemption.',
        'organisms': ['/organisms/human/'],
        'status': 'characterized to standards with exemption',
        'targets': ['/targets/gfp-human/'],
    } in res.json['object']['lot_reviews']


def test_encode3_nontagged_ab_compliant_biosample_char(
    testapp,
    antibody_lot,
    gfp_target,
    immunoblot,
    biosample,
    wrangler,
    document,
    biosample_characterization_compliant,
):
    # Antibody characterization only
    prim_char = testapp.post_json(
        '/antibody_characterization', immunoblot
    ).json['@graph'][0]
    characterization_review = {
        'biosample_ontology': biosample['biosample_ontology'],
        'organism': biosample['organism'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    testapp.patch_json(
        prim_char['@id'],
        {
            'target': gfp_target['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'documents': [document['@id']],
            'characterization_reviews': [characterization_review]
        }
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )

    # With unreviewed biosample characterization
    testapp.patch_json(
        biosample_characterization_compliant['@id'],
        {'antibody': antibody_lot['@id']}
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )


def test_encode3_tagged_ab_unreviewed_biosample_char(
    testapp,
    antibody_lot,
    gfp_target,
    immunoblot,
    biosample,
    wrangler,
    document,
    biosample_characterization_no_review,
):
    testapp.patch_json(antibody_lot['@id'], {'targets': [gfp_target['@id']]})

    # Antibody characterizations only
    prim_char = testapp.post_json(
        '/antibody_characterization', immunoblot
    ).json['@graph'][0]
    characterization_review = {
        'biosample_ontology': biosample['biosample_ontology'],
        'organism': biosample['organism'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    testapp.patch_json(
        prim_char['@id'],
        {
            'target': gfp_target['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'documents': [document['@id']],
            'characterization_reviews': [characterization_review]
        }
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )

    # With unreviewed biosample characterization
    testapp.patch_json(
        biosample_characterization_no_review['@id'],
        {'antibody': antibody_lot['@id']}
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )


def test_encode3_tagged_ab_compliant_biosample_char(
    testapp,
    antibody_lot,
    gfp_target,
    immunoblot,
    biosample,
    wrangler,
    document,
    biosample_characterization_compliant,
):
    testapp.patch_json(antibody_lot['@id'], {'targets': [gfp_target['@id']]})

    # Antibody characterizations only
    prim_char = testapp.post_json(
        '/antibody_characterization', immunoblot
    ).json['@graph'][0]
    characterization_review = {
        'biosample_ontology': biosample['biosample_ontology'],
        'organism': biosample['organism'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    testapp.patch_json(
        prim_char['@id'],
        {
            'target': gfp_target['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'documents': [document['@id']],
            'characterization_reviews': [characterization_review]
        }
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )

    # With compliant biosample characterization
    testapp.patch_json(
        biosample_characterization_compliant['@id'],
        {'antibody': antibody_lot['@id']}
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'characterized to standards'
    assert lot_reviews[0]['detail'] == 'Fully characterized.'


def test_encode3_tagged_ab_exempt_biosample_char(
    testapp,
    antibody_lot,
    gfp_target,
    immunoblot,
    biosample,
    wrangler,
    document,
    biosample_characterization_exempt,
):
    testapp.patch_json(antibody_lot['@id'], {'targets': [gfp_target['@id']]})

    # Antibody characterizations only
    prim_char = testapp.post_json(
        '/antibody_characterization', immunoblot
    ).json['@graph'][0]
    characterization_review = {
        'biosample_ontology': biosample['biosample_ontology'],
        'organism': biosample['organism'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    testapp.patch_json(
        prim_char['@id'],
        {
            'target': gfp_target['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'documents': [document['@id']],
            'characterization_reviews': [characterization_review]
        }
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )

    # With exempt biosample characterization
    testapp.patch_json(
        biosample_characterization_exempt['@id'],
        {'antibody': antibody_lot['@id']}
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == (
        'characterized to standards with exemption'
    )
    assert lot_reviews[0]['detail'] == 'Fully characterized with exemption.'


def test_encode3_tagged_ab_secondary_biosample_char(
    testapp,
    antibody_lot,
    gfp_target,
    immunoblot,
    biosample,
    wrangler,
    document,
    biosample_characterization_2nd_opinion,
):
    testapp.patch_json(antibody_lot['@id'], {'targets': [gfp_target['@id']]})

    # Antibody characterizations only
    prim_char = testapp.post_json(
        '/antibody_characterization', immunoblot
    ).json['@graph'][0]
    characterization_review = {
        'biosample_ontology': biosample['biosample_ontology'],
        'organism': biosample['organism'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    testapp.patch_json(
        prim_char['@id'],
        {
            'target': gfp_target['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'documents': [document['@id']],
            'characterization_reviews': [characterization_review]
        }
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )

    # With secondary opinion biosample characterization
    testapp.patch_json(
        biosample_characterization_2nd_opinion['@id'],
        {'antibody': antibody_lot['@id']}
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )


def test_encode3_tagged_ab_not_compliant_biosample_char(
    testapp,
    antibody_lot,
    gfp_target,
    immunoblot,
    biosample,
    wrangler,
    document,
    biosample_characterization_not_compliant,
):
    testapp.patch_json(antibody_lot['@id'], {'targets': [gfp_target['@id']]})

    # Antibody characterizations only
    prim_char = testapp.post_json(
        '/antibody_characterization', immunoblot
    ).json['@graph'][0]
    characterization_review = {
        'biosample_ontology': biosample['biosample_ontology'],
        'organism': biosample['organism'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    testapp.patch_json(
        prim_char['@id'],
        {
            'target': gfp_target['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'documents': [document['@id']],
            'characterization_reviews': [characterization_review]
        }
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )

    # With non-compliant biosample characterization
    testapp.patch_json(
        biosample_characterization_not_compliant['@id'],
        {'antibody': antibody_lot['@id']}
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )


def test_encode3_tagged_ab_other_exempt_biosample_char(
    testapp,
    antibody_lot,
    gfp_target,
    immunoblot,
    biosample,
    wrangler,
    document,
    biosample_characterization_exempt,
    biosample_2_liver,
):
    testapp.patch_json(antibody_lot['@id'], {'targets': [gfp_target['@id']]})

    # Antibody characterizations only
    prim_char = testapp.post_json(
        '/antibody_characterization', immunoblot
    ).json['@graph'][0]
    characterization_review = {
        'biosample_ontology': biosample['biosample_ontology'],
        'organism': biosample['organism'],
        'lane': 1,
        'lane_status': 'compliant'
    }
    testapp.patch_json(
        prim_char['@id'],
        {
            'target': gfp_target['@id'],
            'status': 'compliant',
            'reviewed_by': wrangler['@id'],
            'documents': [document['@id']],
            'characterization_reviews': [characterization_review]
        }
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 1
    assert lot_reviews[0]['status'] == 'partially characterized'
    assert lot_reviews[0]['detail'] == (
        'Awaiting submission of a compliant secondary characterization.'
    )

    # Different biosamples between antibody characterization and biosample
    # characterization
    testapp.patch_json(
        biosample_characterization_exempt['@id'],
        {'characterizes': biosample_2_liver['@id'], 'antibody': antibody_lot['@id']}
    )
    lot_reviews = testapp.get(
        antibody_lot['@id'] + '@@index-data'
    ).json['object']['lot_reviews']
    assert len(lot_reviews) == 2
    assert {
        "biosample_term_id": "UBERON:0000948",
        "biosample_term_name": "heart",
        "detail": "Awaiting submission of a compliant secondary characterization.",
        "organisms": [
            "/organisms/human/"
        ],
        "status": "partially characterized",
        "targets": [
            "/targets/gfp-human/"
        ]
    } in lot_reviews
    
    assert {
        "biosample_term_id": "UBERON:0002107",
        "biosample_term_name": "liver",
        "detail": "Fully characterized with exemption.",
        "organisms": [
            "/organisms/human/"
        ],
        "status": "characterized to standards with exemption",
        "targets": [
            "/targets/gfp-human/"
        ]
    } in lot_reviews
