import pytest

TEST_HASHES = {
    "test": "Jnh+8wNnELksNFVbxkya8RDrxJNL13dUWTXhp5DCx/quTM2/cYn7azzl2Uk3I2zc",
    "test2": "sh33L5uQeLr//jJULb7mAnbVADkkWZrgcXx97DCacueGtEU5G2HtqUv73UTS0EI0",
    "testing100" * 10: "5rznDSIcDPd/9rjom6P/qkJGtJSV47y/u5+KlkILROaqQ6axhEyVIQTahuBYerLG",
}


@pytest.mark.parametrize(('password', 'pwhash'), TEST_HASHES.items())
def test_edw_hash(password, pwhash):
    from encoded.edw_key import edw_hash
    assert edw_hash(password) == pwhash


def basic_auth(username, password):
    from base64 import b64encode
    return 'Basic ' + b64encode('%s:%s' % (username, password))


@pytest.datafixture
def edw_keys(app):
    from encoded.edw_key import edw_hash
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
            'email': item['email'],
        })
    edw_keys = []
    for n, user in enumerate(users):
        url = '/@@edw_key_create'
        username = 'test_%d' % n
        password = 'password_%d' % n
        pwhash = edw_hash(password)
        item = {'email': user['email'], 'username': username, 'pwhash': pwhash}
        res = testapp.post_json(url, item, status=201)
        edw_keys.append({
            'username': username,
            'password': password,
            'auth_header': basic_auth(username, password),
            'user': user,
        })
    return edw_keys


@pytest.fixture
def edw_key(edw_keys):
    return edw_keys[0]


def test_edw_key_principals(anontestapp, execute_counter, edw_key):
    headers = {'Authorization': edw_key['auth_header']}
    with execute_counter.expect(1):
        res = anontestapp.get('/@@testing-user', headers=headers)

    assert res.json['authenticated_userid'] == 'edwkey:' + edw_key['username']
    assert sorted(res.json['effective_principals']) == [
        'edwkey:' + edw_key['username'],
    ] + edw_key['user']['effective_principals']


def test_edw_key_update(testapp, anontestapp, edw_key):
    from encoded.edw_key import edw_hash
    email = edw_key['user']['email']
    username = edw_key['username']
    password = 'new'
    pwhash = edw_hash(password)
    item = {'email': email, 'username': edw_key['username'], 'pwhash': pwhash}
    url = '/@@edw_key_update'
    testapp.post_json(url, item)

    headers = {'Authorization': edw_key['auth_header']}
    res = anontestapp.get('/@@testing-user', headers=headers)
    assert res.json['authenticated_userid'] is None
    assert res.json['effective_principals'] == ['system.Everyone']

    headers = {'Authorization': basic_auth(username, password)}
    res = anontestapp.get('/@@testing-user', headers=headers)
    assert res.json['authenticated_userid'] == 'edwkey:' + edw_key['username']
    assert sorted(res.json['effective_principals']) == [
        'edwkey:' + edw_key['username'],
    ] + edw_key['user']['effective_principals']


def test_edw_key_current_user(anontestapp, edw_key):
    headers = {'Authorization': edw_key['auth_header']}
    res = anontestapp.get('/@@current-user', headers=headers)
    assert res.json['_links']['labs']
