import pytest

@pytest.fixture
def computational_model(testapp, lab, award):
    return{
        'lab': lab['@id'],
        'award': award['@id'],
        'computational_model_type': 'imputation'
    }


@pytest.fixture
def computational_model_unique_software(computational_model, software_version1, software_version2):
    item = computational_model.copy()
    item.update(
        {
            'software_used': [
                software_version1['@id'],
                software_version2['@id']
            ],
        }
    )
    return item


@pytest.fixture
def computational_model_non_unique_software(computational_model,software_version1, software_version2):
    item = computational_model.copy()
    item.update(
        {
            'software_used': [
                software_version1['@id'],
                software_version2['@id'],
                software_version2['@id']
            ],
        }
    )
    return item
