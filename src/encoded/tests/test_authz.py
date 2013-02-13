import unittest
from pyramid.httpexceptions import HTTPBadRequest
import requests

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(autocommit=False)
        self.config.add_settings({'persona.audiences': 'http://someaudience'})
        self.config.include('encoded.authz')
        self.security_policy = self.config.testing_securitypolicy()
        self.config.set_authorization_policy(self.security_policy)
        self.config.set_authentication_policy(self.security_policy)
        self.config.commit()

    def tearDown(self):
        testing.tearDown()

    def test_login(self):
        from ..authz import login
        data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Fsomeaudience').json()
        email = data['email']
        assertion = data['assertion']

        request = testing.DummyRequest()
        request.params['assertion'] = assertion
        request.params['came_from'] = '/'
        response = login(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.security_policy.remembered, email)

    def test_login_fails_with_bad_audience(self):
        from ..authz import login
        data = requests.get('http://personatestuser.org/email_with_assertion/http%3A%2F%2Fbadaudience').json()
        # email = data['email']
        assertion = data['assertion']

        request = testing.DummyRequest()
        request.params['assertion'] = assertion
        request.params['came_from'] = '/'

        self.assertRaises(HTTPBadRequest, login, request)
        self.assertFalse(hasattr(self.security_policy, 'remembered'))

    def test_logout(self):
        from ..authz import logout
        request = testing.DummyRequest()
        request.params['came_from'] = '/'
        response = logout(request)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.security_policy.forgotten)



