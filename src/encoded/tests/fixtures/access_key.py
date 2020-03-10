import pytest
from ..constants import *


@pytest.fixture
def access_key(testapp, submitter):
    description = 'My programmatic key'
    item = {
        'user': submitter['@id'],
        'description': description,
    }
    res = testapp.post_json('/access_key', item)
    result = res.json['@graph'][0].copy()
    result['secret_access_key'] = res.json['secret_access_key']
    return result

@pytest.fixture
def access_key_1(access_key):
    item = access_key.copy()
    item.update({
        'schema_version': '1'
    })
    return item

@pytest.fixture
def no_login_access_key(testapp, no_login_submitter):
    description = 'My programmatic key'
    item = {
        'user': no_login_submitter['@id'],
        'description': description,
    }
    res = testapp.post_json('/access_key', item)
    result = res.json['@graph'][0].copy()
    result['secret_access_key'] = res.json['secret_access_key']
    return result

