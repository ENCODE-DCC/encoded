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
 

def test_genetic_modification_reagents(testapp, genetic_modification, source):
    res = testapp.get(genetic_modification['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for error in errors.get('WARNING', [])]
    assert any(error['category'] == 'missing genetic modification reagents' for
               error in errors_list)
    testapp.patch_json(genetic_modification['@id'], {'reagents': [
        {
            'source': source['@id'],
            'identifier': 'TRCN0000246247'
        }]})
    res = testapp.get(genetic_modification['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = [error for v in errors.values() for error in v]
    print (errors_list)
    assert all(error['category'] != 'missing genetic modification reagents' for
               error in errors_list)        
   