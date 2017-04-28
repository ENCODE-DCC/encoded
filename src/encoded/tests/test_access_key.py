import pytest


def basic_auth(username, password):
    from base64 import b64encode
    from pyramid.compat import ascii_native_
    return 'Basic ' + ascii_native_(b64encode(('%s:%s' % (username, password)).encode('utf-8')))


def auth_header(access_key):
    return basic_auth(access_key['access_key_id'], access_key['secret_access_key'])


@pytest.fixture
def no_login_submitter(testapp, lab, award):
    item = {
        'first_name': 'ENCODE',
        'last_name': 'Submitter',
        'email': 'no_login_submitter@example.org',
        'submits_for': [lab['@id']],
        'status': 'disabled',
    }
    # User @@object view has keys omitted.
    res = testapp.post_json('/user', item)
    return testapp.get(res.location).json


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


def test_access_key_get(anontestapp, access_key):
    headers = {'Authorization': auth_header(access_key)}
    anontestapp.get('/', headers=headers)


def test_access_key_get_bad_username(anontestapp, access_key):
    headers = {'Authorization': basic_auth('not_an_access_key', 'bad_password')}
    anontestapp.get('/', headers=headers, status=401)


def test_access_key_get_bad_password(anontestapp, access_key):
    headers = {'Authorization': basic_auth(access_key['access_key_id'], 'bad_password')}
    anontestapp.get('/', headers=headers, status=401)


def test_access_key_principals(anontestapp, execute_counter, access_key, submitter, lab):
    headers = {'Authorization': auth_header(access_key)}
    with execute_counter.expect(2):
        res = anontestapp.get('/@@testing-user', headers=headers)

    assert res.json['authenticated_userid'] == 'accesskey.' + access_key['access_key_id']

    assert sorted(res.json['effective_principals']) == [
        'accesskey.%s' % access_key['access_key_id'],
        'group.submitter',
        'lab.%s' % lab['uuid'],
        'submits_for.%s' % lab['uuid'],
        'system.Authenticated',
        'system.Everyone',
        'userid.%s' % submitter['uuid'],
        'viewing_group.ENCODE3',
    ]


def test_access_key_self_create(anontestapp, access_key, submitter):
    extra_environ = {'REMOTE_USER': str(submitter['email'])}
    res = anontestapp.post_json(
        '/access_key/', {}, extra_environ=extra_environ
        )
    access_key_id = res.json['access_key_id']
    headers = {
        'Authorization': basic_auth(access_key_id, res.json['secret_access_key']),
    }
    res = anontestapp.get('/@@testing-user', headers=headers)
    assert res.json['authenticated_userid'] == 'accesskey.' + access_key_id


def test_access_key_submitter_cannot_create_for_someone_else(anontestapp, submitter):
    extra_environ = {'REMOTE_USER': str(submitter['email'])}
    anontestapp.post_json(
        '/access_key/', {'user': 'BOGUS'}, extra_environ=extra_environ, status=422)


def test_access_key_reset(anontestapp, access_key, submitter):
    headers = {'Authorization': auth_header(access_key)}
    extra_environ = {'REMOTE_USER': str(submitter['email'])}  # Must be native string for Python 2.7
    res = anontestapp.post_json(
        access_key['@id'] + '@@reset-secret', {}, extra_environ=extra_environ)
    new_headers = {
        'Authorization': basic_auth(access_key['access_key_id'], res.json['secret_access_key']),
    }
    anontestapp.get('/@@testing-user', headers=headers, status=401)
    res = anontestapp.get('/@@testing-user', headers=new_headers)
    assert res.json['authenticated_userid'] == 'accesskey.' + access_key['access_key_id']


def test_access_key_delete_disable_login(anontestapp, testapp, access_key):
    testapp.patch_json(access_key['@id'], {'status': 'deleted'})
    headers = {'Authorization': auth_header(access_key)}
    anontestapp.get('/@@testing-user', headers=headers, status=401)


def test_access_key_user_disable_login(anontestapp, no_login_access_key):
    access_key = no_login_access_key
    headers = {'Authorization': auth_header(access_key)}
    anontestapp.get('/@@testing-user', headers=headers, status=401)


def test_access_key_edit(anontestapp, access_key):
    headers = {'Authorization': auth_header(access_key)}
    NEW_DESCRIPTION = 'new description'
    properties = {'description': NEW_DESCRIPTION}
    anontestapp.put_json(access_key['@id'], properties, headers=headers)

    res = anontestapp.get(access_key['@id'], properties, headers=headers)
    assert res.json['description'] == NEW_DESCRIPTION


@pytest.mark.parametrize('frame', ['', 'raw', 'edit', 'object', 'embedded', 'page'])
def test_access_key_view_hides_secret_access_key_hash(testapp, access_key, frame):
    query = '?frame=' + frame if frame else ''
    res = testapp.get(access_key['@id'] + query)
    assert 'secret_access_key_hash' not in res.json


def test_access_key_uses_edw_hash(app, access_key):
    from encoded.edw_hash import EDWHash
    from snovault import COLLECTIONS
    root = app.registry[COLLECTIONS]
    obj = root.by_item_type['access_key'][access_key['access_key_id']]
    pwhash = obj.properties['secret_access_key_hash']
    assert EDWHash.encrypt(access_key['secret_access_key']) == pwhash
