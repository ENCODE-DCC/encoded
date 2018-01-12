from snovault import COLLECTIONS
from snovault.calculated import calculate_properties
from snovault.validation import ValidationFailure
from snovault.validators import no_validate_item_content_post
from operator import itemgetter
from pyramid.authentication import CallbackAuthenticationPolicy
import requests
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound,
)
from pyramid.security import (
    NO_PERMISSION_REQUIRED,
    remember,
    forget,
)
from pyramid.settings import (
    asbool,
    aslist,
)
from pyramid.traversal import find_resource
from pyramid.view import (
    view_config,
)


_marker = object()



def includeme(config):
    config.scan(__name__)
    config.add_route('login', 'login')
    config.add_route('logout', 'logout')
    config.add_route('session', 'session')
    config.add_route('session-properties', 'session-properties')
    config.add_route('impersonate-user', 'impersonate-user')


class LoginDenied(HTTPForbidden):
    title = 'Login failure'


class Auth0AuthenticationPolicy(CallbackAuthenticationPolicy):
    """
    Checks assertion during authentication so login can construct user session.
    """
    login_path = '/login'
    method = 'POST'

    def unauthenticated_userid(self, request):

        if request.method != self.method or request.path != self.login_path:
            return None

        cached = getattr(request, '_auth0_authenticated', _marker)
        if cached is not _marker:
            return cached

        try:
            access_token = request.json['accessToken']
        except (ValueError, TypeError, KeyError):
            if self.debug:
                self._log(
                    'Missing assertion.',
                    'unauthenticated_userid',
                    request)
            request._auth0_authenticated = None
            return None
        
        try:
            user_url = "https://{domain}/userinfo?access_token={access_token}" \
                .format(domain='encode.auth0.com', access_token=access_token)

            user_info = requests.get(user_url).json()
        except Exception as e:
            if self.debug:
                self._log(
                    ('Invalid assertion: %s (%s)', (e, type(e).__name__)),
                    'unauthenticated_userid',
                    request)
            request._auth0_authenticated = None
            return None

        if user_info['email_verified'] == True:
            email = request._auth0_authenticated = user_info['email'].lower()
            return email
        else:
            return None


    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []


# Unfortunately, X-Requested-With is not sufficient.
# http://lists.webappsec.org/pipermail/websecurity_lists.webappsec.org/2011-February/007533.html
# Checking the CSRF token in middleware is easier
@view_config(route_name='login', request_method='POST',
             permission=NO_PERMISSION_REQUIRED)
def login(request):
    """View to check the auth0 assertion and remember the user"""
    login = request.authenticated_userid
    if login is None:
        namespace = userid = None
    else:
        namespace, userid = login.split('.', 1)

    if namespace != 'auth0':
        request.session.invalidate()
        request.response.headerlist.extend(forget(request))
        raise LoginDenied()

    request.session.invalidate()
    request.session.get_csrf_token()
    request.response.headerlist.extend(remember(request, 'mailto.' + userid))

    properties = request.embed('/session-properties', as_user=userid)
    if 'auth.userid' in request.session:
        properties['auth.userid'] = request.session['auth.userid']

    return properties


@view_config(route_name='logout',
             permission=NO_PERMISSION_REQUIRED, http_cache=0)
def logout(request):
    """View to forget the user"""
    request.session.invalidate()
    request.session.get_csrf_token()
    request.response.headerlist.extend(forget(request))
    if asbool(request.params.get('redirect', True)):
        raise HTTPFound(location=request.resource_path(request.root))
    return {}


@view_config(route_name='session-properties', request_method='GET',
             permission=NO_PERMISSION_REQUIRED)
def session_properties(request):
    for principal in request.effective_principals:
        if principal.startswith('userid.'):
            break
    else:
        return {}

    namespace, userid = principal.split('.', 1)
    user = request.registry[COLLECTIONS]['user'][userid]
    user_actions = calculate_properties(user, request, category='user_action')

    properties = {
        'user': request.embed(request.resource_path(user)),
        'user_actions': [v for k, v in sorted(user_actions.items(), key=itemgetter(0))],
        'admin': 'group.admin' in request.effective_principals
    }

    if 'auth.userid' in request.session:
        properties['auth.userid'] = request.session['auth.userid']

    return properties


@view_config(route_name='session', request_method='GET',
             permission=NO_PERMISSION_REQUIRED)
def session(request):
    request.session.get_csrf_token()
    return request.session


@view_config(route_name='impersonate-user', request_method='POST',
             validators=[no_validate_item_content_post],
             permission='impersonate')
def impersonate_user(request):
    """As an admin, impersonate a different user."""
    user = request.validated['user']

    try:
        user = find_resource(request.root, user)
    except KeyError:
        raise ValidationFailure('body', ['user'], 'User not found.')

    if user.item_type != 'user':
        raise ValidationFailure('body', ['user'], 'User not found.')
    if user.properties.get('status') != 'current':
        raise ValidationFailure('body', ['user'], 'User is not enabled.')

    request.session.invalidate()
    request.session.get_csrf_token()
    request.response.headerlist.extend(
        remember(request, 'mailto.%s' % user.uuid))
    user_properties = request.embed(
        '/session-properties', as_user=str(user.uuid))
    if 'auth.userid' in request.session:
        user_properties['auth.userid'] = request.session['auth.userid']

    return user_properties
