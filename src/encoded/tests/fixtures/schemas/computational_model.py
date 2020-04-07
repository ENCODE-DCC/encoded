import pytest


@pytest.fixture
def computational_model_url(testapp, lab, award, software_version, software_version2):
    item={
        'accession': "ENCSR860CMZ",
        'lab': lab['@id'],
        'award': award['@id'],
        'computational_model_type': 'imputation',
        'software_used': [
            software_version['@id'],
            software_version2['@id']
        ],
    }
    return testapp.post_json('/computational_model', item, status=201).json['@graph'][0]


@pytest.fixture
def computational_model_for_dup_software_used_url(testapp, lab, award, software_version2):
    item={
        'accession': "ENCSR860CMZ",
        'lab': lab['@id'],
        'award': award['@id'],
        'computational_model_type': 'imputation',
        'software_used': [
            software_version2['@id'],
            software_version2['@id']
        ],
    }
    return testapp.post_json('/computational_model', item, status=201).json['@graph'][0]
