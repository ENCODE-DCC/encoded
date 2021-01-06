import pytest


@pytest.fixture
def dataset_base(testapp, award_base):
    item = {
        'award': award_base['uuid'],
        'status': 'in progress'
    }
    return testapp.post_json('/dataset', item, status=201).json['@graph'][0]
