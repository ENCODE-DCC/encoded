import pytest

@pytest.fixture
def biosample_data(submitter, lab, award, source, human, brain):
    return {
        'award': award['@id'],
        'biosample_ontology': brain['uuid'],
        'lab': lab['@id'],
        'organism': human['@id'],
        'source': source['@id'],
    }


def test_organ_slims(testapp, biosample_data):
    res = testapp.post_json('/biosample', biosample_data)
    location = res.location
    item = testapp.get(location + '?frame=embedded').json
    assert 'brain' in item['biosample_ontology']['organ_slims']
