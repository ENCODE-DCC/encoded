import pytest


@pytest.fixture
def source(testapp):
    item = {
        'name': 'sigma',
        'title': 'Sigma-Aldrich',
        'url': 'http://www.sigmaaldrich.com',
        'status': 'released'
    }
    return testapp.post_json('/source', item).json['@graph'][0]


@pytest.fixture
def source_0():
    return{
        'title': 'Fake source',
        'name': "fake-source"
    }


@pytest.fixture
def source_1(source_0, lab, submitter, award):
    item = source_0.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
        'lab': lab['uuid'],
        'submitted_by': submitter['uuid'],
        'award': award['uuid']
    })
    return item


@pytest.fixture
def source_5(source_0, lab, submitter, award):
    item = source_0.copy()
    item.update({
        'schema_version': '5',
        'status': 'current',
        'lab': lab['uuid'],
        'submitted_by': submitter['uuid'],
        'award': award['uuid']
    })
    return item
