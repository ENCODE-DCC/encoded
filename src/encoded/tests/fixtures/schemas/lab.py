import pytest


@pytest.fixture
def other_lab(testapp):
    item = {
        'title': 'Other lab',
        'name': 'other-lab',
    }
    return testapp.post_json('/lab', item, status=201).json['@graph'][0]


@pytest.fixture
def lab_0_0():
    return{
        'name': 'Fake Lab',
    }


@pytest.fixture
def lab_1_0(lab_0_0):
    item = lab_0_0.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item

@pytest.fixture
def lab(testapp):
    item = {
        'name': 'encode-lab',
        'title': 'ENCODE lab',
    }
    return testapp.post_json('/lab', item).json['@graph'][0]


@pytest.fixture
def remc_lab(testapp):
    item = {
        'name': 'remc-lab',
        'title': 'REMC lab',
    }
    return testapp.post_json('/lab', item).json['@graph'][0]


@pytest.fixture
def encode_lab(testapp):
    item = {
        'name': 'encode-processing-pipeline',
        'title': 'ENCODE Processing Pipeline',
        'status': 'current',
        'uuid': 'a558111b-4c50-4b2e-9de8-73fd8fd3a67d',
        }
    return testapp.post_json('/lab', item, status=201).json['@graph'][0]
