import pytest
import requests
from unittest import mock
from snovault import COLLECTIONS		
import encoded.auth0 as auth0
from jsonschema_serialize_fork.exceptions import ValidationError
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
    HTTPForbidden,
    HTTPUnprocessableEntity,
)
from pyramid.security import (
    remember,
)

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


def _mock_requests_get(**kwargs):
    class MockRequestsGet:

        def __init__(self, kwargs):
            self.json_data = kwargs['json_data']
            self.status_code = kwargs['status_code']

        def json(self):
            return self.json_data
    return MockRequestsGet(kwargs)


@pytest.fixture(scope='session')
def mock_requests_get(**kwargs):
    return _mock_requests_get(**kwargs)


def _mock_request(data={}):
    request = mock.Mock()
    request.json = {
        'accessToken': data.get('accessToken', 'access-token-200-unverified-email'),
    }
    request.registry = {
        COLLECTIONS: {
            'user': mock.Mock(
                return_value={
                    'type_info': {},
                })
        }
    }
    return request


@pytest.fixture(scope='session')
def mock_request(data={}):
    return _mock_request(data)


def _mock_context():
    context = mock.Mock()
    context.type_info.schema = ''
    return context


@pytest.fixture(scope='session')
def mock_context():
    return _mock_context()


def _mock_collection_add(users, request, render):
    result = {
        'status': 'success',
        '@type': ['result'],
        '@graph': [],
    }
    return result


@pytest.fixture(scope='session')
def mock_collection_add(users, request, render):
    return _mock_collection_add(users, request, render)


def _mock_validate_request(schema, request, user_info):
    if not user_info or not user_info['first_name'] or not user_info['last_name'] or not user_info['email']:
        request.errors = ['invalid user info']
    else:
        request.errors = []
    return ''


@pytest.fixture(scope='session')
def mock_validate_request(schema, request, user_info):
    return _mock_validate_request(schema, request, user_info)


def _mock_collection_add_return_none(users, request, render):
    return None


@pytest.fixture(scope='session')
def mock_collection_add_return_none(users, request, render):
    return _mock_collection_add_return_none(users, request, render)


@pytest.fixture(scope='session')
def test_login_no_csrf(anontestapp, auth0_encode_user_token):
    res = anontestapp.post_json('/login', auth0_encode_user_token, status=400)
    assert 'Set-Cookie' in res.headers


def test_login_unknown_user(anontestapp, auth0_encode_user_token):
    res = anontestapp.get('/session')
    csrf_token = str(res.json['_csrft_'])
    headers = {'X-CSRF-Token': csrf_token}
    res = anontestapp.post_json('/login', auth0_encode_user_token, headers=headers, status=403)
    assert 'Set-Cookie' in res.headers


@mock.patch('requests.get', return_value=_mock_requests_get(url='', json_data={}, status_code=400))
def test_signup_verify_invalid_status_code_throws_exception(mock_get):
    with pytest.raises(HTTPBadRequest):
        request = _mock_request()
        context = _mock_context()
        auth0.signup(context, request)


@mock.patch('requests.get', return_value=_mock_requests_get(url='', json_data={'email_verified':False,}, status_code=400))
def test_signup_verify_unauthenticated_email_causes_exception(mock_get):
    with pytest.raises(HTTPBadRequest):
        request = _mock_request()
        context = _mock_context()
        auth0.signup(context, request)


@mock.patch('requests.get', return_value=_mock_requests_get(url='', json_data={'email_verified':False,}, status_code=400))
def test_signup_verify_not_providing_access_token_raises_exception(mock_get):
    with pytest.raises(HTTPBadRequest):
        request = _mock_request({'accessToken': None})
        context = _mock_context()
        auth0.signup(context, request)



@pytest.mark.parametrize('json_data', [{
    'email_verified': True,
    'email': 'fakeemail@email.com',
    'first_name': 'fakefirstname',
    'last_name': 'fakelastname',
}, {
    'email_verified': True,
    'email': 'fakeemail@email.com',
    'given_name': 'fakegivenName',
    'family_name': 'fakefamilyname',
}, {
    'email_verified': True,
    'email': 'fakeemail@email.com',
    'name': 'fakefirstame fakelastname',
}, {
    'email_verified': True,
    'email': 'fakeemail@email.com',
    'name': 'fakefirstame',
}])
@mock.patch('encoded.auth0.validate_request', side_effect=_mock_validate_request)
@mock.patch('encoded.auth0.collection_add', side_effect=_mock_collection_add)
@mock.patch('requests.get')
def test_signup_verify_account_is_created(mock_get, mock_collection_add, mock_validate_request, json_data):
    request = _mock_request()
    request.errors = []
    context = _mock_context()
    mock_get.return_value = _mock_requests_get(
        url='',
        json_data=json_data,
        status_code=200
    )
    expected = {'@graph': [], '@type': ['result'], 'status': 'success'}
    signup = auth0.signup(context, request)
    assert len(request.errors) == 0
    assert signup == expected


@pytest.mark.parametrize('json_data', [{
    'email_verified': True,
    'email': None,
    'first_name': 'fakefirstname',
    'last_name': '',
}, {
    'email_verified': True,
    'email': '',
    'first_name': '',
    'last_name': None,
}, {
    'email_verified': True,
    'email': 'fakeemail@email.com',
    'first_name': '',
    'last_name': 'fakelastname',
}, {
    'email_verified': True,
    'email': None,
    'given_name': 'givenName',
    'family_name': '',
}, {
    'email_verified': True,
    'email': '',
    'given_name': 'givenName',
    'family_name': '',
}, {
    'email_verified': True,
    'email': 'fakeemail@email.com',
    'given_name': '',
    'family_name': 'familyname',
}, {
    'email_verified': True,
    'email': '',
    'given_name': '',
    'family_name': '',
}, {
    'email_verified': True,
    'email': None,
    'given_name': '',
    'family_name': '',
}, {
    'email_verified': True,
    'email': 'fakeemail@email.com',
    'name': '',
}, {
    'email_verified': True,
    'email': None,
    'name': '',
}, {
    'email_verified': True,
    'email': '',
    'name': '',
}, {
    'email_verified': True,
    'email': 'fakeemail@email.com',
    'name': '   ',
}, {
    'email_verified': True,
    'email': '',
    'name': 'name',
}])
@mock.patch('encoded.auth0.validate_request', side_effect=_mock_validate_request)
@mock.patch('encoded.auth0.collection_add', side_effect=_mock_collection_add)
@mock.patch('requests.get')
def test_signup_fails_if_given_improper_credentials(mock_get, mock_collection_add, mock_validate_request, json_data):
    with pytest.raises(ValidationError):
        request = _mock_request()
        mock_get.return_value = _mock_requests_get(
            url='',
            json_data=json_data,
            status_code=200
        )
        request.errors = []
        context = _mock_context()
        signup = auth0.signup(context, request)


@pytest.mark.parametrize('json_data, expected', [
    ({
        'email': 'fakeemail@email.com',
        'first_name': 'fakefirstname',
        'last_name': 'fakelastname',
    }, {
        'email': 'fakeemail@email.com',
        'first_name': 'fakefirstname',
        'last_name': 'fakelastname',
    }),
    ({
        'email': 'fakeemail@email.com',
        'given_name': 'fakegivenName',
        'family_name': 'fakefamilyname',
    }, {
        'email': 'fakeemail@email.com',
        'first_name': 'fakegivenName',
        'last_name': 'fakefamilyname',
    }),
    ({
        'email': 'fakeemail@email.com',
        'name': 'fakefirstname fakelastname',
    }, {
        'email': 'fakeemail@email.com',
        'first_name': 'fakefirstname',
        'last_name': 'fakelastname',
    }),
    ({
        'email': 'fakeemail@email.com',
        'name': 'fakefirstname',
    }, {
        'email': 'fakeemail@email.com',
        'first_name': 'fakefirstname',
        'last_name': 'fakeemail',
    }),
    ])
def test_get_user_info_assigns_valid_data_properly(json_data, expected):
    user_info = auth0._get_user_info(json_data)
    assert user_info['email'] == expected['email']
    assert user_info['first_name'] == expected['first_name']
    assert user_info['last_name'] == expected['last_name']



@pytest.mark.parametrize('json_data, expected', [
    (None, None,),
    ({}, None),
    ({
        'email': None,
        'first_name': 'fakefirstname',
        'last_name': 'fakeemail',
    }, None),
    ({
        'email': '',
        'first_name': 'fakefirstname',
        'last_name': 'fakeemail',
    }, None),
    ({
        'email': '    ',
        'first_name': 'fakefirstname',
        'last_name': 'fakeemail',
    }, None),
    ])
def test_get_user_info_throws_proper_exception(json_data, expected):
    with pytest.raises(ValidationError):
        user_info = auth0._get_user_info(json_data)
    

@mock.patch('encoded.auth0.validate_request', side_effect=_mock_validate_request)
@mock.patch('encoded.auth0.collection_add', side_effect=_mock_collection_add)
@mock.patch('requests.get', return_value=_mock_requests_get(
    url='',
    json_data={
        'email_verified': True,
        'email': 'fakeemail@email.com',
        'given_name': 'fakefirstname',
        'family_name': 'fakelastname',
    },
    status_code=200,))
def test_signup_verify_email_is_verified_with_given_and_family_name(mock_get, mock_collection_add, mock_validate_request):
    request = _mock_request()
    request.errors = []
    context = _mock_context()
    signup = auth0.signup(context, request)
    expected = {'@graph': [], 'status': 'success', '@type': ['result']}
    assert signup == expected


@mock.patch('encoded.auth0.validate_request', side_effect=_mock_validate_request)
@mock.patch('encoded.auth0.collection_add', side_effect=_mock_collection_add)
@mock.patch('requests.get', return_value=_mock_requests_get(
    url='',
    json_data={
        'email_verified': True,
        'email': 'fakeemail@email.com',
        'name': 'michael jackson',
    },
    status_code=200,))
def test_signup_verify_email_is_verified_with_name(mock_get, mock_collection_add, mock_validate_request):
    request = _mock_request()
    request.errors = []
    context = _mock_context()
    expected = {'@graph': [], 'status': 'success', '@type': ['result']}
    signup = auth0.signup(context, request)
    assert signup == expected



@mock.patch('encoded.auth0.validate_request', side_effect=_mock_validate_request)
@mock.patch('encoded.auth0.collection_add', side_effect=_mock_collection_add_return_none)
@mock.patch('requests.get', return_value=_mock_requests_get(
    url='',
    json_data={
        'email_verified': True,
        'email': 'fakeemail@email.com',
        'first_name': 'fakefirstname',
        'last_name': 'fakelastname',
    },
    status_code=200,))
def test_signup_verify_exception_thrown_if_user_is_not_created(mock_get, mock_collection_add_return_none, mock_validate_request):
    with pytest.raises(HTTPInternalServerError):
        request = _mock_request()
        request.errors = ['Smooth Criminal']
        context = _mock_context()
        signup = auth0.signup(context, request)



@mock.patch('encoded.auth0.forget', return_value='')
@mock.patch('encoded.auth0.remember', return_value='')
@mock.patch('encoded.auth0.signup', return_value='userid-uuid')
@mock.patch('requests.get', return_value=_mock_requests_get(
    url='',
    json_data={
        'email_verified': True,
        'email': 'fakeemail@email.com',
        'first_name': 'fakefirstname',
        'last_name': 'fakelastname',
    },
    status_code=200,))
def test_login_throws_proper_exception_when_user_does_not_exist(mock_get, signup, remember, forget):
    class Session:
        def __init__(self):
            self.lst = ['a']
            self.idx = 0
            self.session = mock.Mock(return_value=[])
            self.invalidate = mock.Mock()
            self.get_csrf_token = mock.Mock()
        def __iter__(self):
            return self

        def __next__(self):
            # iteration is irrelevant
            raise StopIteration()
    request_mock = mock.Mock()
    request_mock.authenticated_userid = '12334.34433'
    request_mock.session = Session()
    request_mock.session.invalidate.return_value = False
    request_mock.session.get_csrf_token.return_value = True
    request_mock.response.headerlist = []
    request_mock.embed.return_value = 'embed-result'
    with pytest.raises(HTTPForbidden):
        login = auth0.login(request_mock)


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


def test_getting_first_and_last_name_from_name():
    name = 'Michael Jackson'
    first_name, last_name = auth0._get_first_and_last_names_from_name(name)
    assert first_name == 'Michael'
    assert last_name == 'Jackson'


def test_getting_first_and_last_name_from_name_no_email():
    name = 'Michael Jackson'
    first_name, last_name = auth0._get_first_and_last_names_from_name(name)
    assert first_name == 'Michael'
    assert last_name == 'Jackson'


def test_getting_first_from_name_when_last_not_provided():
    name = 'Michael'
    first_name, last_name = auth0._get_first_and_last_names_from_name(name)
    assert first_name == 'Michael'
    assert last_name == None


def test_getting_name_if_no_name_not_provided():
    name = ''
    first_name, last_name = auth0._get_first_and_last_names_from_name(name)
    assert first_name is None
    assert last_name is None


def test_getting_name_if_none_name_not_provided():
    name = None
    first_name, last_name = auth0._get_first_and_last_names_from_name(name)
    assert first_name is None
    assert last_name is None



def test_impersonate_user(anontestapp, admin, submitter):
    res = anontestapp.post_json(
        '/impersonate-user', {'user': submitter['@id']},
        extra_environ={'REMOTE_USER': str(admin['email'])}, status=200)
    assert 'Set-Cookie' in res.headers
    assert res.json['auth.userid'] == submitter['uuid']
    res = anontestapp.get('/session')
    assert res.json['auth.userid'] == submitter['uuid']
