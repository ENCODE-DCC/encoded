import pytest
from ..constants import *


@pytest.fixture
def lab(testapp):
    item = {
        'name': 'encode-lab',
        'title': 'ENCODE lab',
    }
    return testapp.post_json('/lab', item).json['@graph'][0]

@pytest.fixture
def lab_0():
    return{
        'name': 'Fake Lab',
    }


@pytest.fixture
def lab_1(lab_0):
    item = lab_0.copy()
    item.update({
        'schema_version': '1',
        'status': 'CURRENT',
    })
    return item