import pytest
from ..constants import *


@pytest.fixture
def ucsc_browser_composite(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
    }
    return testapp.post_json('/ucsc_browser_composite', item).json['@graph'][0]

