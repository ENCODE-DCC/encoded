import pytest


def test_organ_slims(testapp, biosample_ontology_slim):
    res = testapp.post_json('/biosample', biosample_ontology_slim)
    location = res.location
    item = testapp.get(location + '?frame=embedded').json
    assert 'brain' in item['biosample_ontology']['organ_slims']
