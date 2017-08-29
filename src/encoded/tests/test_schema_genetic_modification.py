import pytest


@pytest.fixture
def crispr_deletion(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'deletion',
        'purpose': 'repression',
        'modification_technique': 'CRISPR'
    }


@pytest.fixture
def tale_deletion(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'deletion',
        'purpose': 'repression',
        'modification_technique': 'TALE'
    }


@pytest.fixture
def crispr_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'insertion',
        'purpose': 'tagging',
        'modification_technique': 'CRISPR'
    }


@pytest.fixture
def bombardment_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'insertion',
        'purpose': 'tagging',
        'modification_technique': 'bombardment'
    }


@pytest.fixture
def recomb_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'insertion',
        'purpose': 'tagging',
        'modification_technique': 'site-specific recombination'
    }


@pytest.fixture
def transfection_tag(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'insertion',
        'purpose': 'tagging',
        'modification_technique': 'stable transfection'
    }


@pytest.fixture
def crispri(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'interference',
        'purpose': 'repression',
        'modification_technique': 'CRISPR'
    }


@pytest.fixture
def rnai(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'interference',
        'purpose': 'repression',
        'modification_technique': 'RNAi'
    }


@pytest.fixture
def mutagen(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'mutagenesis',
        'purpose': 'repression',
        'modification_technique': 'mutagen treatment'
    }


@pytest.fixture
def tale_replacement(lab, award):
    return {
        'lab': lab['@id'],
        'award': award['@id'],
        'modification_type': 'replacement',
        'purpose': 'validation',
        'modification_technique': 'TALE'
    }


def test_crispr_deletion_missing_site(testapp, crispr_deletion):
    # modified_site_(by_target_id|by_coordinates|by_sequence) must be specified for deletions
    res = testapp.post_json('/genetic_modification', crispr_deletion, expect_errors=True)
    assert res.status_code == 422


def test_crispr_deletion_two_sites(testapp, crispr_deletion, target):
    # modified_site_(by_target_id|by_coordinates|by_sequence) must be specified for deletions but 
    # no more than one since we can't verify they agree with each other
    crispr_deletion.update({'modified_site_by_target_id': target['@id'],
                            'guide_rna_sequences': ['ACCGGAGA']})
    res = testapp.post_json('/genetic_modification', crispr_deletion, expect_errors=True)
    assert res.status_code == 201
    crispr_deletion = res.json['@graph'][0]
    res = testapp.patch_json(crispr_deletion['@id'], 
                             {'modified_site_by_sequence': 'ACTAAGC'}, expect_errors=True)
    assert res.status_code == 422


def test_tale_deletion_no_RVD_sequence_or_reagent_availability(testapp, tale_deletion, source):
    # TALE modifications either need RVD sequence and/or reagent_availability properties specified
    tale_deletion.update({'modified_site_by_coordinates': 
                          {'assembly': 'hg19', 'start': 88943, 'end': 123829, 'chromosome': 'chr3'}})
    res = testapp.post_json('/genetic_modification', tale_deletion, expect_errors=True)
    assert res.status_code == 422
    '''
    Once the TALE metadata is fixed, we can add the RVD_sequence_pairs dependency back into the schema
    tale_deletion.update({'RVD_sequence_pairs': 
                           [{'left_RVD_sequence': 'NH,NI,NG', 'right_RVD_sequence': 'NN,NG,NI'},
                            {'left_RVD_sequence': 'NN,NH,NH', 'right_RVD_sequence': 'NN,NI,NI'}]})
    '''
    tale_deletion.update({'reagent_availability': [{'repository': source['@id'], 'identifier': '12345'}]})
    res = testapp.post_json('/genetic_modification', tale_deletion, expect_errors=True)
    assert res.status_code == 201


def test_tag_modifications_without_tag(testapp, crispr_tag, bombardment_tag, transfection_tag, 
                                       recomb_tag, target, source, document):
    # We shouldn't allow purpose = tagging if modification_type != insertion
    crispr_tag.update({'modified_site_by_target_id': target['@id'],
                       'guide_rna_sequences': ['ATTAGGCAT'],
                       'epitope_tags': [{'name': 'eGFP', 'location': 'C-terminal'}],
                       'modification_type': 'deletion'})
    res = testapp.post_json('/genetic_modification', crispr_tag, expect_errors=True)
    assert res.status_code == 422
    crispr_tag.update({'modification_type': 'replacement'})
    res = testapp.post_json('/genetic_modification', crispr_tag, expect_errors=True)
    assert res.status_code == 422
    crispr_tag.update({'modification_type': 'mutagenesis'})
    res = testapp.post_json('/genetic_modification', crispr_tag, expect_errors=True)
    assert res.status_code == 422
    crispr_tag.update({'modification_type': 'interference'})
    res = testapp.post_json('/genetic_modification', crispr_tag, expect_errors=True)
    assert res.status_code == 422
    crispr_tag.update({'modification_type': 'insertion'})
    res = testapp.post_json('/genetic_modification', crispr_tag, expect_errors=True)
    assert res.status_code == 201

    # No objects with purpose = tagging should be allowed without epitope_tags property
    bombardment_tag.update({'modified_site_by_target_id': target['@id'],
                            'modified_site_nonspecific': 'random',
                            'modification_type': 'insertion',
                            'documents': [document['@id']]})
    res = testapp.post_json('/genetic_modification', bombardment_tag, expect_errors=True)
    assert res.status_code == 422
    bombardment_tag.update({'epitope_tags': [{'name': 'eGFP', 'location': 'C-terminal'}]})
    res = testapp.post_json('/genetic_modification', bombardment_tag, expect_errors=True)
    assert res.status_code == 201

    recomb_tag.update({'modified_site_by_target_id': target['@id'],
                       'modified_site_nonspecific': 'random',
                       'modification_type': 'insertion',
                       'documents': [document['@id']]})
    res = testapp.post_json('/genetic_modification', recomb_tag, expect_errors=True)
    assert res.status_code == 422
    recomb_tag.update({'epitope_tags': [{'name': 'eGFP', 'location': 'C-terminal'}]})
    res = testapp.post_json('/genetic_modification', recomb_tag, expect_errors=True)
    assert res.status_code == 201

    # Additionally, documents and/or reagent_availability must be provided for transfection, 
    # bombardment etc.
    transfection_tag.update({'modified_site_by_target_id': target['@id'],
                             'modification_type': 'insertion'})
    res = testapp.post_json('/genetic_modification', transfection_tag, expect_errors=True)
    assert res.status_code == 422
    transfection_tag.update({'epitope_tags': [{'name': 'eGFP', 'location': 'C-terminal'}]})
    res = testapp.post_json('/genetic_modification', transfection_tag, expect_errors=True)
    assert res.status_code == 422
    transfection_tag.update({'documents': [document['@id']]})
    res = testapp.post_json('/genetic_modification', transfection_tag, expect_errors=True)
    assert res.status_code == 201
    transfection_tag.update({'reagent_availability': [{'repository': source['@id'], 
                                                       'identifier': '12345'}]})
    res = testapp.post_json('/genetic_modification', transfection_tag, expect_errors=True)
    assert res.status_code == 201


def test_crispri_properties(testapp, crispri, target, source, document):
    # It doesn't make sense to specify a CRISPRi target by sequence when you should be 
    # doing it by target id, so it's not allowed.
    crispri.update({'modified_site_by_sequence': 'TTTCATAGAC',
                    'guide_rna_sequences': ['CATTAGGTAT'],
                    'documents': [document['@id']]})
    res = testapp.post_json('/genetic_modification', crispri, expect_errors=True)
    assert res.status_code == 422
    del crispri['modified_site_by_sequence']
    crispri.update({'modified_site_by_target_id': target['@id']})
    res = testapp.post_json('/genetic_modification', crispri, expect_errors=True)
    assert res.status_code == 201

    # You shouldn't be able to add epitope_tags, introduced_sequence, rnai_sequences etc.
    # to a CRISPRi modification
    crispri = res.json['@graph'][0]
    res = testapp.patch_json(crispri['@id'],
                             {'epitope_tags': [{'name': 'eGFP', 'location': 'C-terminal'}]}, expect_errors=True)
    assert res.status_code == 422
    res = testapp.patch_json(crispri['@id'], {'rnai_sequences': ['ATTACTAG', 'TTGCACTATA']}, expect_errors=True)
    assert res.status_code == 422
    res = testapp.patch_json(crispri['@id'], {'introduced_sequence': 'CTATATAGGGAT'}, expect_errors=True)
    assert res.status_code == 422
    res = testapp.patch_json(crispri['@id'], {'RVD_sequence_pair': [{'left_RVD_sequence': 'NN,NN,NN', 
                                                                     'right_RVD_sequecne': 'NI,NI,NH'}]},
                                                                      expect_errors=True)
    assert res.status_code == 422
    # Adding reagent_availability on top of having guide_rna_sequences and documents should be allowed
    res = testapp.patch_json(crispri['@id'], {'reagent_availability': 
                                              [{'repository': source['@id'], 'identifier': '54321'}]}, 
                                              expect_errors=True)
    assert res.status_code == 200


def test_rnai_properties(testapp, rnai, target, source, document):
    # RNAi modifications should have modification_type = interference and purpose = repression
    rnai.update({'modification_type': 'deletion', 'rnai_sequences': ['ATTACG'], 
                 'modified_site_by_target_id': target['@id']})
    res = testapp.post_json('/genetic_modification', rnai, expect_errors=True)
    assert res.status_code == 422
    rnai.update({'modification_type': 'replacement'})
    res = testapp.post_json('/genetic_modification', rnai, expect_errors=True)
    assert res.status_code == 422
    rnai.update({'modification_type': 'mutagenesis'})
    res = testapp.post_json('/genetic_modification', rnai, expect_errors=True)
    assert res.status_code == 422
    rnai.update({'modification_type': 'insertion'})
    res = testapp.post_json('/genetic_modification', rnai, expect_errors=True)
    assert res.status_code == 422
    rnai.update({'modification_type': 'interference', 'purpose': 'activation'})
    res = testapp.post_json('/genetic_modification', rnai, expect_errors=True)
    assert res.status_code == 422
    rnai.update({'purpose': 'overexpression'})
    res = testapp.post_json('/genetic_modification', rnai, expect_errors=True)
    assert res.status_code == 422
    rnai.update({'purpose': 'tagging'})
    res = testapp.post_json('/genetic_modification', rnai, expect_errors=True)
    assert res.status_code == 422

    # RNAi modifications require RNAi_sequences and/or reagent_availability to be specified
    rnai.update({'purpose': 'repression'})
    res = testapp.post_json('/genetic_modification', rnai, expect_errors=True)
    assert res.status_code == 201
    rnai = res.json['@graph'][0]
    res = testapp.patch_json(rnai['@id'], {'reagent_availability': 
                                           [{'repository': source['@id'], 'identifier': 'abc'}]})
    assert res.status_code == 200


def test_mutagen_properties(testapp, mutagen, target, treatment, document):
    # Modifications by mutagen treatment should have non-specific modified sites
    mutagen.update({'modified_site_by_target_id': target['@id'], 'treatments': [treatment['@id']]})
    res = testapp.post_json('/genetic_modification', mutagen, expect_errors=True)
    assert res.status_code == 422
    del mutagen['modified_site_by_target_id']
    mutagen.update({'modified_site_by_sequence': 'ATTATGACAT', 'treatments': [treatment['@id']]})
    res = testapp.post_json('/genetic_modification', mutagen, expect_errors=True)
    assert res.status_code == 422
    del mutagen['modified_site_by_sequence']
    mutagen.update({'modified_site_by_coordinates': 
                    {'assembly': 'GRCh38', 'start': 383892, 'end': 482980, 'chromosome': 'chr11'},
                     'treatments': [treatment['@id']]})
    res = testapp.post_json('/genetic_modification', mutagen, expect_errors=True)
    assert res.status_code == 422
    del mutagen['modified_site_by_coordinates']
    mutagen.update({'modified_site_nonspecific': 'random', 'treatments': [treatment['@id']]})
    res = testapp.post_json('/genetic_modification', mutagen, expect_errors=True)
    assert res.status_code == 201


def test_tale_replacement_properties(testapp, tale_replacement, source):
    # Replacement modifications need to include introduced_sequence
    tale_replacement.update({'modified_site_by_sequence': 'ATTTTAGGCAGGTAGGATTACGAGGACCCAGGTACGATCAGGT',
                             'reagent_availability': [{'repository': source['@id'], 'identifier': 'xyz'}]})
    res = testapp.post_json('/genetic_modification', tale_replacement, expect_errors=True)
    assert res.status_code == 422
    tale_replacement.update({'introduced_sequence': 'TTATCGATCGATTTGAGCATAGAAATGGCCGATTTATATGCCCGA'})
    res = testapp.post_json('/genetic_modification', tale_replacement, expect_errors=True)
    assert res.status_code == 201
