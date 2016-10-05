import pytest


def auth0_access_token():
    import requests
    fb_access_token = {
        'connection': 'Username-Password-Authentication',
        'scope': 'openid',
        'client_id': 'WIOr638GdDdEGPJmABPhVzMn6SYUIdIH',
        'grant_type': 'password',
        'username': 'test@encodeproject.org',
        'password': 'test'
    }
    url = 'https://encode.auth0.com/oauth/ro'
    try:
        res = requests.post(url, data=fb_access_token)
        res.raise_for_status()
    except Exception as e:
        pytest.skip("Error retrieving auth0 fb test user access token: %r" % e)
    data = res.json()
    if 'access_token' not in data:
        pytest.skip("Missing 'access_token' in persona test user access token: %r" % data)
    return data['access_token']


@pytest.fixture(scope='session')
def auth0_encode_user():
    access_token = auth0_access_token()
    return {'accessToken': access_token}



def test_login_no_csrf(anontestapp, auth0_encode_user):
    res = anontestapp.post_json('/login', auth0_encode_user, status=400)
    assert 'Set-Cookie' in res.headers


def test_login_unknown_user(anontestapp, auth0_encode_user):
    res = anontestapp.get('/session')
    csrf_token = str(res.json['_csrft_'])
    headers = {'X-CSRF-Token': csrf_token}
    res = anontestapp.post_json('/login', auth0_encode_user, headers=headers, status=403)
    assert 'Set-Cookie' in res.headers


# def test_login_bad_audience(anontestapp, persona_bad_assertion):
#     res = anontestapp.get('/session')
#     csrf_token = str(res.json['_csrft_'])
#     headers = {'X-CSRF-Token': csrf_token}
#     res = anontestapp.post_json('/login', persona_bad_assertion, headers=headers, status=403)
#     assert 'Set-Cookie' in res.headers


# def test_login_logout(testapp, anontestapp, persona_assertion):
#     # Create a user with the persona email
#     url = '/users/'
#     email = persona_assertion['email']
#     item = {
#         'email': email,
#         'first_name': 'Persona',
#         'last_name': 'Test User',
#     }
#     testapp.post_json(url, item, status=201)

#     # Log in
#     res = anontestapp.get('/session')
#     csrf_token = str(res.json['_csrft_'])
#     headers = {'X-CSRF-Token': csrf_token}
#     res = anontestapp.post_json('/login', persona_assertion, headers=headers, status=200)
#     assert 'Set-Cookie' in res.headers
#     res = anontestapp.get('/session')
#     assert res.json['auth.userid'] == email

#     # Log out
#     res = anontestapp.get('/logout?redirect=false', headers=headers, status=200)
#     assert 'Set-Cookie' in res.headers
#     res = anontestapp.get('/session')
#     assert 'auth.userid' not in res.json


# def test_impersonate_user(anontestapp, admin, submitter):
#     res = anontestapp.post_json(
#         '/impersonate-user', {'userid': submitter['email']},
#         extra_environ={'REMOTE_USER': str(admin['email'])}, status=200)
#     assert 'Set-Cookie' in res.headers
#     assert res.json['auth.userid'] == submitter['email']
#     res = anontestapp.get('/session')
#     assert res.json['auth.userid'] == submitter['email']
