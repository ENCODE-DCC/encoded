import pytest


@pytest.fixture
def base_functional_characterization_series(testapp, lab, fcc_posted_CRISPR_screen, award):
    item = {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'related_datasets': [
            fcc_posted_CRISPR_screen['@id']
        ]
    }
    return testapp.post_json('/functional_characterization_series', item, status=201).json['@graph'][0]

@pytest.fixture
def functional_characterization_series_3(testapp, lab, fcc_posted_CRISPR_screen, award):
    return {
        'award': award['uuid'],
        'lab': lab['uuid'],
        'schema_version': '3',
        'related_datasets': [
            fcc_posted_CRISPR_screen['@id']
        ]
    }
