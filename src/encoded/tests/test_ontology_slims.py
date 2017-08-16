import pytest

@pytest.fixture
def biosample(submitter, lab, award, source, human):
    return {
        'award': award['@id'],
        'biosample_term_id': 'UBERON:0000955',
        'biosample_term_name': 'brain',
        'biosample_type': 'tissue',
        'lab': lab['@id'],
        'organism': human['@id'],
        'source': source['@id'],
    }


def test_organ_slims(testapp, biosample):
    res = testapp.post_json('/biosample', biosample)
    location = res.location
    item = testapp.get(location + '?frame=object').json
    assert 'brain' in item['organ_slims']
