import pytest


def basic_auth(username, password):
    from base64 import b64encode
    from pyramid.compat import ascii_native_
    return 'Basic ' + ascii_native_(b64encode(('%s:%s' % (username, password)).encode('utf-8')))


@pytest.yield_fixture(scope='session')
def access_keys(app, connection):
    tx = connection.begin_nested()
    from webtest import TestApp
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)
    from .sample_data import URL_COLLECTION
    lab_name = {}
    for item in URL_COLLECTION['lab']:
        res = testapp.post_json('/lab', item, status=201)
        lab_name[item['name']] = item['uuid']
        lab_name[item['uuid']] = item['uuid']

    users = []
    for item in URL_COLLECTION['user']:
        res = testapp.post_json('/user', item, status=201)
        principals = [
            'system.Authenticated',
            'system.Everyone',
            'userid.' + item['uuid'],
        ]
        principals.extend('lab.%s' % lab_name[name] for name in item['submits_for'])
        principals.extend('submits_for.%s' % lab_name[name] for name in item['submits_for'])
        principals.extend('group.%s' % group for group in item.get('groups', []))
        if item['submits_for']:
            principals.append('group.submitter')
        users.append({
            'location': res.location,
            'effective_principals': sorted(principals),
            'uuid': item['uuid'],
            'email': item['email'],
        })
    access_keys = []
    for user in users:
        description = 'My programmatic key'
        item = {'user': user['uuid'], 'description': description}
        res = testapp.post_json('/access_key', item, status=201)
        access_keys.append({
            'location': res.location,
            'access_key_id': res.json['access_key_id'],
            'secret_access_key': res.json['secret_access_key'],
            'auth_header': basic_auth(res.json['access_key_id'], res.json['secret_access_key']),
            'description': description,
            'user': user,
        })
    yield access_keys
    tx.rollback()


@pytest.fixture
def access_key(access_keys):
    return access_keys[0]


@pytest.fixture
def no_login_access_key(access_keys):
    return access_keys[-1]


def test_access_key_current_user(anontestapp, access_key):
    headers = {'Authorization': access_key['auth_header']}
    res = anontestapp.get('/@@current-user', headers=headers)
    assert res.json['submits_for']


def test_access_key_get(anontestapp, access_key):
    headers = {'Authorization': access_key['auth_header']}
    anontestapp.get('/', headers=headers)


def test_access_key_get_bad_username(anontestapp, access_key):
    headers = {'Authorization': basic_auth('not_an_access_key', 'bad_password')}
    anontestapp.get('/', headers=headers, status=401)


def test_access_key_get_bad_password(anontestapp, access_key):
    headers = {'Authorization': basic_auth(access_key['access_key_id'], 'bad_password')}
    anontestapp.get('/', headers=headers, status=401)


def test_access_key_principals(anontestapp, execute_counter, access_key):
    headers = {'Authorization': access_key['auth_header']}
    with execute_counter.expect(2):
        res = anontestapp.get('/@@testing-user', headers=headers)

    assert res.json['authenticated_userid'] == 'accesskey.' + access_key['access_key_id']
    assert sorted(res.json['effective_principals']) == [
        'accesskey.' + access_key['access_key_id'],
    ] + access_key['user']['effective_principals']


def test_access_key_reset(anontestapp, access_key):
    headers = {'Authorization': access_key['auth_header']}
    extra_environ = {'REMOTE_USER': str(access_key['user']['email'])}
    res = anontestapp.post_json(
        access_key['location'] + '@@reset-secret', {}, extra_environ=extra_environ)
    new_headers = {
        'Authorization': basic_auth(access_key['access_key_id'], res.json['secret_access_key']),
    }
    anontestapp.get('/@@testing-user', headers=headers, status=401)
    res = anontestapp.get('/@@testing-user', headers=new_headers)
    assert res.json['authenticated_userid'] == 'accesskey.' + access_key['access_key_id']


def test_access_key_disable(anontestapp, access_key):
    headers = {'Authorization': access_key['auth_header']}
    extra_environ = {'REMOTE_USER': str(access_key['user']['email'])}
    anontestapp.post_json(
        access_key['location'] + '@@disable-secret', {}, extra_environ=extra_environ)
    anontestapp.get('/@@testing-user', headers=headers, status=401)


def test_access_key_user_disable_login(anontestapp, no_login_access_key):
    access_key = no_login_access_key
    headers = {'Authorization': access_key['auth_header']}
    anontestapp.get('/@@testing-user', headers=headers, status=401)


def test_access_key_edit(anontestapp, access_key):
    headers = {'Authorization': access_key['auth_header']}
    NEW_DESCRIPTION = 'new description'
    properties = {'description': NEW_DESCRIPTION}
    anontestapp.put_json(access_key['location'], properties, headers=headers)

    res = anontestapp.get(access_key['location'], properties, headers=headers)
    assert res.json['description'] == NEW_DESCRIPTION


@pytest.mark.parametrize('frame', ['', 'raw', 'edit', 'object', 'embedded'])
def test_access_key_view_hides_secret_access_key_hash(anontestapp, access_key, frame):
    query = '?frame=' + frame if frame else ''
    headers = {'Authorization': access_key['auth_header']}
    res = anontestapp.get(access_key['location'] + query, headers=headers)
    assert 'secret_access_key_hash' not in res.json


def test_access_key_uses_edw_hash(app, access_key):
    from encoded.edw_hash import EDWHash
    from encoded.contentbase import LOCATION_ROOT
    root = app.registry[LOCATION_ROOT]
    obj = root.by_item_type['access_key'][access_key['access_key_id']]
    pwhash = obj.properties['secret_access_key_hash']
    assert EDWHash.encrypt(access_key['secret_access_key']) == pwhash
