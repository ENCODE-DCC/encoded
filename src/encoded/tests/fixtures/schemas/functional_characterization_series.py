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
