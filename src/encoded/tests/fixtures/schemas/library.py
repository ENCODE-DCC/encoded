import pytest


@pytest.fixture
def library_base(testapp, lab_base, dataset_base, library_protocol_base, suspension_base):
    item = {
        'lab': lab_base['uuid'],
        'dataset': dataset_base['uuid'],
        'protocol': library_protocol_base['uuid'],
        'derived_from': [suspension_base['uuid']]
    }
    return testapp.post_json('/library', item, status=201).json['@graph'][0]
