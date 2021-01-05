import pytest
from webtest import AppError

def basic_auth(username, password):
    from base64 import b64encode
    from pyramid.compat import ascii_native_
    return 'Basic ' + ascii_native_(b64encode(('%s:%s' % (username, password)).encode('utf-8')))


def auth_header(access_key_3):
    return basic_auth(access_key_3['access_key_id'], access_key_3['secret_access_key'])

def test_access_key_get(anontestapp, access_key_3):
    headers = {'Authorization': auth_header(access_key_3)}
    anontestapp.get('/', headers=headers)


def test_access_key_get_bad_username(anontestapp, access_key_3):
    headers = {'Authorization': basic_auth('not_an_access_key', 'bad_password')}
    anontestapp.get('/', headers=headers, status=401)


def test_access_key_get_bad_password(anontestapp, access_key_3):
    headers = {'Authorization': basic_auth(access_key_3['access_key_id'], 'bad_password')}
    anontestapp.get('/', headers=headers, status=401)


def test_access_key_self_create_by_verified_member(anontestapp, verified_member):
    extra_environ = {'REMOTE_USER': str(verified_member['email'])}
    res = anontestapp.post_json(
        '/access_key/', {}, extra_environ=extra_environ
        )
    access_key_id = res.json['access_key_id']
    headers = {
        'Authorization': basic_auth(access_key_id, res.json['secret_access_key']),
    }
    res = anontestapp.get('/@@testing-user', headers=headers)
    assert res.json['authenticated_userid'] == 'accesskey.' + access_key_id


def test_access_key_self_create_by_unverified_member(anontestapp, unverified_member):
    with pytest.raises(AppError):
        extra_environ = {'REMOTE_USER': str(unverified_member['email'])}
        res = anontestapp.post_json(
            '/access_key/', {}, extra_environ=extra_environ
        )


def test_access_key_self_create_by_admin(anontestapp, admin):
    extra_environ = {'REMOTE_USER': str(admin['email'])}
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


def test_access_key_reset(anontestapp, access_key_3, submitter):
    headers = {'Authorization': auth_header(access_key_3)}
    extra_environ = {'REMOTE_USER': str(submitter['email'])}  # Must be native string for Python 2.7
    res = anontestapp.post_json(
        access_key_3['@id'] + '@@reset-secret', {}, extra_environ=extra_environ)
    new_headers = {
        'Authorization': basic_auth(access_key_3['access_key_id'], res.json['secret_access_key']),
    }
    anontestapp.get('/@@testing-user', headers=headers, status=401)
    res = anontestapp.get('/@@testing-user', headers=new_headers)
    assert res.json['authenticated_userid'] == 'accesskey.' + access_key_3['access_key_id']


def test_access_key_delete_disable_login(anontestapp, testapp, access_key_3):
    testapp.patch_json(access_key_3['@id'], {'status': 'deleted'})
    headers = {'Authorization': auth_header(access_key_3)}
    anontestapp.get('/@@testing-user', headers=headers, status=401)


def test_access_key_user_disable_login(anontestapp, no_login_access_key):
    access_key = no_login_access_key
    headers = {'Authorization': auth_header(access_key)}
    anontestapp.get('/@@testing-user', headers=headers, status=401)


def test_access_key_edit(anontestapp, access_key_3):
    headers = {'Authorization': auth_header(access_key_3)}
    NEW_DESCRIPTION = 'new description'
    properties = {'description': NEW_DESCRIPTION}
    anontestapp.put_json(access_key_3['@id'], properties, headers=headers)

    res = anontestapp.get(access_key_3['@id'], properties, headers=headers)
    assert res.json['description'] == NEW_DESCRIPTION


@pytest.mark.parametrize('frame', ['', 'raw', 'edit', 'object', 'embedded', 'page'])
def test_access_key_view_hides_secret_access_key_hash(testapp, access_key_3, frame):
    query = '?frame=' + frame if frame else ''
    res = testapp.get(access_key_3['@id'] + query)
    assert 'secret_access_key_hash' not in res.json


def test_access_key_uses_edw_hash(app, access_key_3):
    from encoded.edw_hash import EDWHash
    from snovault import COLLECTIONS
    root = app.registry[COLLECTIONS]
    obj = root.by_item_type['access_key'][access_key_3['access_key_id']]
    pwhash = obj.properties['secret_access_key_hash']
    assert EDWHash.hash(access_key_3['secret_access_key']) == pwhash
