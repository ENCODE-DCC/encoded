import unittest

class TestACLAuthorizationPolicy(unittest.TestCase):
    def _getTargetClass(self):
        from ..local_roles import LocalRolesAuthorizationPolicy
        return LocalRolesAuthorizationPolicy

    def _makeOne(self):
        return self._getTargetClass()()

    def _makeResources(self):
        from pyramid.security import Deny
        from pyramid.security import Allow
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        from pyramid.security import ALL_PERMISSIONS
        from pyramid.security import DENY_ALL
        root = DummyContext()
        community = DummyContext(__name__='community', __parent__=root)
        blog = DummyContext(__name__='blog', __parent__=community)
        root.__acl__ = [
            (Allow, 'role.member', VIEW),
            ]
        root.__ac_local_roles__ = {
            'someguy': ['role.member'],
            }
        community.__acl__ = [
            (Allow, 'role.admin', ALL_PERMISSIONS),
            (Allow, 'role.member', MEMBER_PERMS),
            (Allow, 'role.reader', VIEW),
            DENY_ALL,
            ]
        community.__ac_local_roles_block__ = True
        community.__ac_local_roles__ = {
            'fred': ['role.admin'],
            'wilma': ['role.reader'],
            }
        blog.__ac_local_roles__ = {
            'barney': ['role.member'],
            'wilma': ['role.reader'],
            }

        return root, community, blog

    def test_class_implements_IAuthorizationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthorizationPolicy
        verifyClass(IAuthorizationPolicy, self._getTargetClass())

    def test_instance_implements_IAuthorizationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthorizationPolicy
        verifyObject(IAuthorizationPolicy, self._makeOne())

    def test_permits(self):
        from pyramid.security import Deny
        from pyramid.security import Allow
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        from pyramid.security import ALL_PERMISSIONS
        from pyramid.security import DENY_ALL

        root, community, blog = self._makeResources()
        policy = self._makeOne()

        result = policy.permits(blog, [Everyone, Authenticated, 'wilma'],
                                'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'role.reader', VIEW))
        self.assertEqual(result.acl, community.__acl__)

        result = policy.permits(blog, [Everyone, Authenticated, 'wilma'],
                                'delete')
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = policy.permits(blog, [Everyone, Authenticated, 'fred'], 'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'role.admin', ALL_PERMISSIONS))
        result = policy.permits(blog, [Everyone, Authenticated, 'fred'],
                                'doesntevenexistyet')
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'role.admin', ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

        result = policy.permits(blog, [Everyone, Authenticated, 'barney'],
                                'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Allow, 'role.member', MEMBER_PERMS))
        result = policy.permits(blog, [Everyone, Authenticated, 'barney'],
                                'administer')
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)
        
        result = policy.permits(root, [Everyone, Authenticated, 'someguy'],
                                'view')
        self.assertEqual(result, True)
        self.assertEqual(result.context, root)
        self.assertEqual(result.ace, (Allow, 'role.member', VIEW))
        result = policy.permits(blog,
                                [Everyone, Authenticated, 'someguy'], 'view')
        self.assertEqual(result, False)
        self.assertEqual(result.context, community)
        self.assertEqual(result.ace, (Deny, Everyone, ALL_PERMISSIONS))
        self.assertEqual(result.acl, community.__acl__)

    def test_principals_allowed_by_permission(self):
        from pyramid.security import Allow
        from pyramid.security import Deny
        from pyramid.security import DENY_ALL
        from pyramid.security import ALL_PERMISSIONS

        root, community, blog = self._makeResources()
        policy = self._makeOne()
        
        result = sorted(policy.principals_allowed_by_permission(blog, VIEW))
        self.assertEqual(result, ['barney', 'fred', 'role.admin', 'role.member', 'role.reader', 'wilma'])
        result = sorted(policy.principals_allowed_by_permission(community,
            VIEW))
        self.assertEqual(result, ['fred', 'role.admin', 'role.member', 'role.reader', 'wilma'])
        result = sorted(policy.principals_allowed_by_permission(community,
            VIEW))
        result = sorted(policy.principals_allowed_by_permission(root, VIEW))
        self.assertEqual(result, ['role.member', 'someguy'])

    def test_callable_ac_local_roles(self):
        from pyramid.security import Allow
        context = DummyContext()
        context.__acl__ = [(Allow, 'role.reader', 'read')]
        fn = lambda self: {'bob': ['role.reader']}
        context.__ac_local_roles__ = fn.__get__(context, context.__class__)
        policy = self._makeOne()
        result = policy.permits(context, ['bob'], 'read')
        self.assertTrue(result)

    def test_string_ac_local_roles(self):
        from pyramid.security import Allow
        context = DummyContext()
        context.__acl__ = [(Allow, 'role.reader', 'read')]
        context.__ac_local_roles__ = {'bob': 'role.reader'}
        policy = self._makeOne()
        result = policy.permits(context, ['bob'], 'read')
        self.assertTrue(result)


class DummyContext:
    def __init__(self, *arg, **kw):
        self.__dict__.update(kw)


VIEW = 'view'
EDIT = 'edit'
CREATE = 'create'
DELETE = 'delete'
MODERATE = 'moderate'
ADMINISTER = 'administer'
COMMENT = 'comment'

GUEST_PERMS = (VIEW, COMMENT)
MEMBER_PERMS = GUEST_PERMS + (EDIT, CREATE, DELETE)
MODERATOR_PERMS = MEMBER_PERMS + (MODERATE,)
ADMINISTRATOR_PERMS = MODERATOR_PERMS + (ADMINISTER,)
