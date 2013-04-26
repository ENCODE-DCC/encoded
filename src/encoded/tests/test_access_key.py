import pytest

@pytest.fixture
def users(testapp):
    from .sample_data import URL_COLLECTION
    url = '/users/'
    users = []
    for item in URL_COLLECTION[url]:
        res = testapp.post_json(url, item, status=201)
        principals = [
            'system.Authenticated',
            'system.Everyone',
            'userid:' + item['_uuid'],
        ]
        principals.extend('lab:' + lab_uuid for lab_uuid in item['lab_uuids'])
        users.append({
            'location': res.location,
            'effective_principals': sorted(principals),
            '_uuid': item['_uuid'],
        })
    return users


@pytest.fixture
def user(users):
    return users[0]


@pytest.fixture
def access_keys(testapp, users):
    from base64 import b64encode
    access_keys = []
    for user in users:
        description = 'My programmatic key'
        url = '/access-keys/'
        item = {'user_uuid': user['_uuid'], 'description': description}
        res = testapp.post_json(url, item, status=201)
        access_keys.append({
            'location': res.location,
            'access_key_id': res.json['access_key_id'],
            'secret_access_key': res.json['secret_access_key'],
            'auth_header': 'Basic ' + b64encode(
                '%s:%s' % (res.json['access_key_id'], res.json['secret_access_key'])),
            'user_uuid': user['_uuid'],
            'description': description,
            'user': user,
        })
    return access_keys


@pytest.fixture
def access_key(access_keys):
    return access_keys[0]


def test_access_key_post(anontestapp, execute_counter, access_key):
    headers = {'Authorization': access_key['auth_header']}
    with execute_counter.expect(2):
        res = anontestapp.get('/@@testing-user', headers=headers)

    assert res.json['authenticated_userid'] == 'accesskey:' + access_key['access_key_id']
    assert sorted(res.json['effective_principals']) == [
        'accesskey:' + access_key['access_key_id'],
    ] + access_key['user']['effective_principals']

    res = anontestapp.get(access_key['location'], headers=headers)
    assert 'description' in res.json
    #assert 'secret_access_key_hash' not in res.json
