import pytest


@pytest.fixture
def sequencing_run_base(testapp, library_base):
    item = {
        'derived_from': [library_base['uuid']],
        'uuid': '41b4ba77-44e4-4496-b293-1c2225e2d600'
    }
    return testapp.post_json('/sequencing_run', item, status=201).json['@graph'][0]
