import pytest

@pytest.fixture
def biosample(submitter, lab, award, source, human, brain):
    return {
        'award': award['@id'],
        'biosample_ontology': brain['uuid'],
        'lab': lab['@id'],
        'organism': human['@id'],
        'source': source['@id'],
    }


def test_organ_slims(testapp, biosample):
    res = testapp.post_json('/biosample', biosample)
    location = res.location
    item = testapp.get(location + '?frame=embedded').json
    assert 'brain' in item['biosample_ontology']['organ_slims']
