import pytest


@pytest.fixture
def genetic_modification(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'modified_site_by_coordinates': {
            'assembly': 'GRCh38',
            'chromosome': '11',
            'start': 20000,
            'end': 21000
        },
        'purpose': 'repression',
        'category': 'deletion',
        'method': 'CRISPR',
        'zygosity': 'homozygous'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def genetic_modification_RNAi(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'modified_site_by_coordinates': {
            'assembly': 'GRCh38',
            'chromosome': '11',
            'start': 20000,
            'end': 21000
        },
        'purpose': 'repression',
        'category': 'deletion',
        'method': 'RNAi'
    }
    return testapp.post_json('/genetic_modification', item).json['@graph'][0]


@pytest.fixture
def tagged_target(testapp, gene):
    item = {
        'genes': [gene['uuid']],
        'modifications': [{'modification': 'eGFP'}],
        'label': 'eGFP-CTCF',
        'investigated_as': ['recombinant protein', 'transcription factor']
    }
    return testapp.post_json('/target', item, status=201).json['@graph'][0]


def test_genetic_modification_reagents(testapp, genetic_modification, source):
    res = testapp.get(genetic_modification['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing genetic modification reagents' for
               error in errors_list)
    testapp.patch_json(genetic_modification['@id'], {'reagents': [
        {
            'source': source['@id'],
            'identifier': 'TRCN0000246247'
        }]})
    res = testapp.get(genetic_modification['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing genetic modification reagents' for
               error in errors_list)


def test_genetic_modification_reagents_fly(testapp, genetic_modification_RNAi, fly_donor):
    res = testapp.get(genetic_modification_RNAi['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'missing genetic modification reagents' for
               error in errors_list)
    testapp.patch_json(fly_donor['@id'], {'genetic_modifications': [genetic_modification_RNAi['@id']]})
    res = testapp.get(genetic_modification_RNAi['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert all(error['category'] != 'missing genetic modification reagents' for
               error in errors_list)


def test_genetic_modification_target(testapp, construct_genetic_modification,
                                     tagged_target):
    testapp.patch_json(construct_genetic_modification['@id'],
                       {'modified_site_by_target_id': tagged_target['@id']})
    res = testapp.get(construct_genetic_modification['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'target already modified' for
               error in errors_list)
