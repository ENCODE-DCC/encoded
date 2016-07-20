import pytest

@pytest.fixture(scope='session')
def test_user():
    return {'username': 'user@test.com', 'password': 'test'}


def test_login_unknown_user(anontestapp, test_user):
    res = anontestapp.post_json('/login', test_user, status=403)

def test_invalid_create_user(testapp):
    url = '/users/'
    item = {
        'emailllll': 'blah@blah.com',
        'first_name': 'Persona',
        'last_name': 'Test User',
        'password' : 'password'
    }
    resp = testapp.post_json(url, item, status=422)
    print(resp)
    assert resp.json['errors'] is not None


def test_login_logout(testapp, anontestapp, app_settings, test_user):
    # Create a user with the test_users email
    url = '/users/'
    item = {
        'email': test_user['username'],
        'first_name': 'Persona',
        'last_name': 'Test User',
        'password' : test_user['password']
    }
    testapp.post_json(url, item, status=201)

    # Log in
    login = {'username' : item['email'], 'password': item['password']}
    res = anontestapp.post_json('/login', login, status=200)
    assert 'Set-Cookie' in res.headers
    assert res.json['auth.userid'] == login['username']

    # Log out
    res = anontestapp.get('/logout?redirect=false', status=200)
    assert 'Set-Cookie' in res.headers
    assert 'auth.userid' not in res.json

def test_impersonate_user(anontestapp, admin, submitter):
    res = anontestapp.post_json(
        '/impersonate-user', {'userid': submitter['email']},
        extra_environ={'REMOTE_USER': str(admin['email'])}, status=200)
    assert 'Set-Cookie' in res.headers
    assert res.json['auth.userid'] == submitter['email']
    res = anontestapp.get('/session-properties')
    assert res.json['auth.userid'] == submitter['email']
