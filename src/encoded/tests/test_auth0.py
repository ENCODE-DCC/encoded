import pytest
import requests

@pytest.fixture(scope='session')
def auth0_access_token():
    creds = {
        'connection': 'Username-Password-Authentication',
        'scope': 'openid',
        'client_id': 'WIOr638GdDdEGPJmABPhVzMn6SYUIdIH',
        'grant_type': 'password',
        'username': 'test@encodeproject.org',
        'password': 'test'
    }
    url = 'https://encode.auth0.com/oauth/ro'
    try:
        res = requests.post(url, data=creds)
        res.raise_for_status()
    except Exception as e:
        pytest.skip("Error retrieving auth0 test user access token: %r" % e)
    data = res.json()
    if 'access_token' not in data:
        pytest.skip("Missing 'access_token' in auth0 test user access token: %r" % data)
    return data['access_token']


@pytest.fixture(scope='session')
def auth0_encode_user_token(auth0_access_token):
    return {'accessToken': auth0_access_token}

@pytest.fixture(scope='session')
def auth0_encode_user_profile(auth0_access_token):
    user_url = "https://{domain}/userinfo?access_token={access_token}" \
        .format(domain='encode.auth0.com', access_token=auth0_access_token)
    user_info = requests.get(user_url).json()
    return user_info


def test_login_no_csrf(anontestapp, auth0_encode_user_token):
    res = anontestapp.post_json('/login', auth0_encode_user_token, status=400)
    assert 'Set-Cookie' in res.headers


def test_login_unknown_user(anontestapp, auth0_encode_user_token):
    res = anontestapp.get('/session')
    csrf_token = str(res.json['_csrft_'])
    headers = {'X-CSRF-Token': csrf_token}
    res = anontestapp.post_json('/login', auth0_encode_user_token, headers=headers, status=403)
    assert 'Set-Cookie' in res.headers



def test_login_logout(testapp, anontestapp, auth0_encode_user_token, auth0_encode_user_profile):
    # Create a user with the persona email
    url = '/users/'
    email = auth0_encode_user_profile['email']
    item = {
        'email': email,
        'first_name': 'Auth0',
        'last_name': 'Test User',
    }
    testapp.post_json(url, item, status=201)

    # Log in
    res = anontestapp.get('/session')
    csrf_token = str(res.json['_csrft_'])
    headers = {'X-CSRF-Token': csrf_token}
    res = anontestapp.post_json('/login', auth0_encode_user_token, headers=headers, status=200)
    assert 'Set-Cookie' in res.headers
    res = anontestapp.get('/session')
    assert res.json['auth.userid'] == email

    # Log out
    res = anontestapp.get('/logout?redirect=false', headers=headers, status=200)
    assert 'Set-Cookie' in res.headers
    res = anontestapp.get('/session')
    assert 'auth.userid' not in res.json


def test_impersonate_user(anontestapp, admin, submitter):
    res = anontestapp.post_json(
        '/impersonate-user', {'user': submitter['@id']},
        extra_environ={'REMOTE_USER': str(admin['email'])}, status=200)
    assert 'Set-Cookie' in res.headers
    assert res.json['auth.userid'] == submitter['uuid']
    res = anontestapp.get('/session')
    assert res.json['auth.userid'] == submitter['uuid']
