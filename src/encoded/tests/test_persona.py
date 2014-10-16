import pytest

pytestmark = [
    pytest.mark.persona,
    pytest.mark.slow,
]


def persona_test_data(audience):
    import requests
    from urllib import quote
    url = 'http://personatestuser.org/email_with_assertion/%s' % quote(audience, '')
    try:
        res = requests.get(url)
        res.raise_for_status()
    except Exception as e:
        pytest.skip("Error retrieving persona test user: %r" % e)
    data = res.json()
    if 'email' not in data:
        pytest.skip("Missing 'email' in persona test user: %r" % data)
    return data


@pytest.fixture(scope='session')
def persona_assertion(app_settings):
    audience = app_settings['persona.audiences']
    return persona_test_data(audience)


@pytest.fixture(scope='session')
def persona_bad_assertion():
    return persona_test_data('http://badaudience')


def test_login_no_csrf(anontestapp, persona_assertion):
    res = anontestapp.post_json('/login', persona_assertion, status=400)
    assert 'Set-Cookie' in res.headers


def test_login_unknown_user(anontestapp, persona_assertion):
    res = anontestapp.get('/session')
    csrf_token = str(res.json['_csrft_'])
    headers = {'X-CSRF-Token': csrf_token}
    res = anontestapp.post_json('/login', persona_assertion, headers=headers, status=403)
    assert 'Set-Cookie' in res.headers


def test_login_bad_audience(anontestapp, persona_bad_assertion):
    res = anontestapp.get('/session')
    csrf_token = str(res.json['_csrft_'])
    headers = {'X-CSRF-Token': csrf_token}
    res = anontestapp.post_json('/login', persona_bad_assertion, headers=headers, status=403)
    assert 'Set-Cookie' in res.headers


def test_login_logout(testapp, anontestapp, persona_assertion):
    # Create a user with the persona email
    url = '/users/'
    email = persona_assertion['email']
    item = {
        'email': email,
        'first_name': 'Persona',
        'last_name': 'Test User',
    }
    testapp.post_json(url, item, status=201)

    # Log in
    res = anontestapp.get('/session')
    csrf_token = str(res.json['_csrft_'])
    headers = {'X-CSRF-Token': csrf_token}
    res = anontestapp.post_json('/login', persona_assertion, headers=headers, status=200)
    assert 'Set-Cookie' in res.headers
    res = anontestapp.get('/session')
    assert res.json['auth.userid'] == email

    # Log out
    res = anontestapp.get('/logout?redirect=false', headers=headers, status=200)
    assert 'Set-Cookie' in res.headers
    res = anontestapp.get('/session')
    assert 'auth.userid' not in res.json
