import unittest
from pyramid.testing import DummyRequest


class TestNamespacedAuthenticationPolicy(unittest.TestCase):
    """ This is a modified version of TestRemoteUserAuthenticationPolicy
    """
    def _getTargetClass(self):
        from snovault.authentication import NamespacedAuthenticationPolicy
        return NamespacedAuthenticationPolicy

    def _makeOne(self, namespace='user',
                base='pyramid.authentication.RemoteUserAuthenticationPolicy',
                *args, **kw):
        return self._getTargetClass()(namespace, base, *args, **kw)

    def test_class_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthenticationPolicy
        klass = self._makeOne().__class__
        verifyClass(IAuthenticationPolicy, klass)

    def test_instance_implements_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_unauthenticated_userid_returns_None(self):
        request = DummyRequest()
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid(self):
        request = DummyRequest(environ={'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'user.fred')

    def test_authenticated_userid_None(self):
        request = DummyRequest()
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid(self):
        request = DummyRequest(environ={'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), 'user.fred')

    def test_effective_principals_None(self):
        from pyramid.security import Everyone
        request = DummyRequest()
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        request = DummyRequest(environ={'REMOTE_USER':'fred'})
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request),
                         [Everyone, Authenticated, 'user.fred'])

    def test_remember(self):
        request = DummyRequest(environ={'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.remember(request, 'fred')
        self.assertEqual(result, [])

    def test_forget(self):
        request = DummyRequest(environ={'REMOTE_USER':'fred'})
        policy = self._makeOne()
        result = policy.forget(request)
        self.assertEqual(result, [])

    # From TestSessionAuthenticationPolicy

    def test_session_remember(self):
        request = DummyRequest()
        policy = self._makeOne(
                    base='pyramid.authentication.SessionAuthenticationPolicy',
                    prefix='')
        result = policy.remember(request, 'user.fred')
        self.assertEqual(request.session.get('userid'), 'fred')
        self.assertEqual(result, [])
        self.assertEqual(policy.unauthenticated_userid(request), 'user.fred')

    def test_session_forget(self):
        request = DummyRequest(session={'userid':'fred'})
        policy = self._makeOne(
                    base='pyramid.authentication.SessionAuthenticationPolicy',
                    prefix='')
        result = policy.forget(request)
        self.assertEqual(request.session.get('userid'), None)
        self.assertEqual(result, [])

    def test_session_forget_no_identity(self):
        request = DummyRequest()
        policy = self._makeOne(
                    base='pyramid.authentication.SessionAuthenticationPolicy',
                    prefix='')
        result = policy.forget(request)
        self.assertEqual(request.session.get('userid'), None)
        self.assertEqual(result, [])
