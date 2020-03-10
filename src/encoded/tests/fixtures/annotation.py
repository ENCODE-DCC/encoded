import pytest
from ..constants import *


@pytest.fixture
def annotation_dataset(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'annotation_type': 'imputation'
    }
    return testapp.post_json('/annotation', item).json['@graph'][0]
