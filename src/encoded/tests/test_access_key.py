import pytest


def basic_auth(username, password):
    from base64 import b64encode
    return 'Basic ' + b64encode('%s:%s' % (username, password))


@pytest.datafixture
def access_keys(app):
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)
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
            'auth_header': basic_auth(res.json['access_key_id'], res.json['secret_access_key']),
            'user_uuid': user['_uuid'],
            'description': description,
            'user': user,
        })
    return access_keys


@pytest.fixture
def access_key(access_keys):
    return access_keys[0]


def test_access_key_principals(anontestapp, execute_counter, access_key):
    headers = {'Authorization': access_key['auth_header']}
    with execute_counter.expect(2):
        res = anontestapp.get('/@@testing-user', headers=headers)

    assert res.json['authenticated_userid'] == 'accesskey:' + access_key['access_key_id']
    assert sorted(res.json['effective_principals']) == [
        'accesskey:' + access_key['access_key_id'],
    ] + access_key['user']['effective_principals']


def test_access_key_reset(anontestapp, access_key):
    headers = {'Authorization': access_key['auth_header']}
    res = anontestapp.post_json(access_key['location'] + '/@@reset-secret', {}, headers=headers)
    new_headers = {'Authorization': basic_auth(access_key['access_key_id'], res.json['secret_access_key'])}

    res = anontestapp.get('/@@testing-user', headers=headers)
    assert res.json['authenticated_userid'] is None

    res = anontestapp.get('/@@testing-user', headers=new_headers)
    assert res.json['authenticated_userid'] == 'accesskey:' + access_key['access_key_id']


def test_access_key_disable(anontestapp, access_key):
    headers = {'Authorization': access_key['auth_header']}
    res = anontestapp.post_json(access_key['location'] + '/@@disable-secret', {}, headers=headers)

    res = anontestapp.get('/@@testing-user', headers=headers)
    assert res.json['authenticated_userid'] is None


def test_access_key_edit(anontestapp, access_key):
    headers = {'Authorization': access_key['auth_header']}
    NEW_DESCRIPTION = 'new description'
    properties = {'description': NEW_DESCRIPTION}
    anontestapp.post_json(access_key['location'], properties, headers=headers)

    res = anontestapp.get(access_key['location'], properties, headers=headers)
    assert res.json['description'] == NEW_DESCRIPTION


def test_access_key_view_hides_secret_access_key_hash(anontestapp, access_key):
    headers = {'Authorization': access_key['auth_header']}
    res = anontestapp.get(access_key['location'], headers=headers)
    assert 'secret_access_key_hash' not in res.json
