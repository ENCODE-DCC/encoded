import pytest

@pytest.fixture
def computational_model(testapp, lab, award):
    item = {
        'lab': lab['@id'],
        'award': award['@id'],
        'computational_model_type': 'imputation'
    }
    return testapp.post_json('/computational_model', item).json['@graph'][0]


@pytest.fixture
def computational_model_unique_software(computational_model):
    item = computational_model.copy()
    item.update(
        {
            'software_used': [
                'software_0',
                'software_1'
            ]
        }
    )
    return item


@pytest.fixture
def computational_model_non_unique_software(computational_model):
    item = computational_model.copy()
    item.update(
        {
            'software_used': [
                'software_0',
                'software_0'
            ]
        }
    )
