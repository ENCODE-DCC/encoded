import pytest
import unittest
from pyramid.httpexceptions import HTTPBadRequest
import requests

from pyramid import testing


@pytest.mark.persona
@pytest.mark.slow
class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config.add_settings({'persona.audiences': 'http://someaudience'})
        self.config.include('encoded.persona')
        self.security_policy = self.config.testing_securitypolicy()
        self.config.set_authorization_policy(self.security_policy)
        self.config.set_authentication_policy(self.security_policy)
        self.config.commit()

    def tearDown(self):
        testing.tearDown()

    def test_login(self):
        from ..persona import login
        data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Fsomeaudience').json()
        if data.get('message', None) == 'Cannot get verified email for assertion':
            self.skipTest("Persona: %s" % data['message'])

        email = data['email']
        assertion = data['assertion']

        req = testing.DummyRequest(json_body={'assertion': assertion, 'came_from': '/'})
        response = login(req)

        self.assertEqual(response['status'], "okay")
        self.assertEqual(response['audience'], self.config.get_settings()['persona.audiences'])
        self.assertEqual(response['email'], email)
        self.assertEqual(response['issuer'], 'login.persona.org')
        self.assertEqual(self.security_policy.remembered, 'mailto:' + email)

    def test_login_fails_with_bad_audience(self):
        from ..persona import login
        data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Fbadaudience').json()

        if data.get('message', None) == 'Cannot get verified email for assertion':
            self.skipTest("Persona: %s" % data['message'])

        assertion = data['assertion']

        req = testing.DummyRequest(json_body={'assertion': assertion, 'came_from': '/'})

        self.assertRaises(HTTPBadRequest, login, req)
        self.assertFalse(hasattr(self.security_policy, 'remembered'))

    def test_logout(self):
        from ..persona import logout
        req = testing.DummyRequest(json_body={'came_from': '/'})
        req.params['came_from'] = '/'
        response = logout(req)

        #self.assertEqual(response.status_code, 200)
        self.assertTrue(self.security_policy.forgotten)


@pytest.mark.persona
@pytest.mark.slow
def test_bad_audience(testapp, dummy_request):
    import requests

    data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Fsomeaudience').json()
    try:
        assertion = data['assertion']
    except KeyError:
        pytest.skip(data.get('message', "Unknown persona error"))

    res = testapp.post_json('/login', params={'assertion': assertion, 'came_from': '/'}, status=400)


def _test_login_cycle(testapp, dummy_request):
    import requests
    from pyramid.security import authenticated_userid

    data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Flocalhost:6543').json()
    try:
        email = data['email']
        assertion = data['assertion']
    except KeyError:
        pytest.skip(data.get('message', "Unknown persona error"))

    res = testapp.post_json('/login', params={'assertion': assertion, 'came_from': '/'}, status=200)

    assert res.json_body['status'] == "okay"
    #assert res.vary == 'Accept'  res.vary or res.headers['vary'] does not exist
    #assert res.cookies['auth_tkt'] != ''  ## or something.
    ## assert testapp.security_policy.remembered == email

    res2 = testapp.get('/users/', status=200)
    '''
    I clearly don't understand the testapp.testResponse
    import sys
    sys.stderr.write(res2)
    assert res2.cookies['auth_tkt'] != ''  ## or something.
    '''
    assert res2.body.startswith('<!DOCTYPE html>')
