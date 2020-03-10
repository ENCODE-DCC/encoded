import pytest
from ..constants import *


@pytest.fixture
def source(testapp):
    item = {
        'name': 'sigma',
        'title': 'Sigma-Aldrich',
        'url': 'http://www.sigmaaldrich.com',
        'status': 'released'
    }
    return testapp.post_json('/source', item).json['@graph'][0]


