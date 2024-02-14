from snovault import COLLECTIONS
from snovault.calculated import calculate_properties
from snovault.validation import ValidationFailure
from snovault.validators import no_validate_item_content_post
from operator import itemgetter
from snovault.crud_views import collection_add
from snovault.schema_utils import validate_request
from pyramid.authentication import CallbackAuthenticationPolicy
from encoded.types.user import User
from jsonschema_serialize_fork.exceptions import ValidationError
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
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
import requests


_marker = object()


def includeme(config):
    config.scan(__name__)
    config.add_route('signup', 'signup')
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
            domain = 'encode.auth0.com'
            user_url = "https://{domain}/userinfo?access_token={access_token}" \
                .format(domain=domain, access_token=access_token)
            user_info = requests.get(user_url).json()
        except Exception as e:
            if self.debug:
                self._log(
                    ('Invalid assertion: %s (%s)', (e, type(e).__name__)),
                    'unauthenticated_userid',
                    request)
            request._auth0_authenticated = None
            return None

        if user_info['email_verified'] is True:
            email = request._auth0_authenticated = user_info['email'].lower()
            return email
        else:
            return None


    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []


@view_config(context=User.Collection, request_method='POST', permission='signup', name='sign-up')
def signup(context, request):
    """
    Create new user.

    :param request: Pyramid request object
    """
    domain = 'encode.auth0.com'
    access_token = request.json.get('accessToken')
    if not access_token:
        raise HTTPBadRequest(explanation='Access token required')
    url = 'https://{domain}/userinfo?access_token={access_token}'.format(domain=domain, access_token=access_token)
    user_data_request = requests.get(url)
    if user_data_request.status_code != 200:
        raise HTTPBadRequest(explanation='Could not get user data')
    user_data = user_data_request.json()
    if user_data['email_verified'] is not True:
        raise HTTPBadRequest(explanation='Unverified email')
    user_info = _get_user_info(user_data)
    validate_request(context.type_info.schema, request, user_info)
    if request.errors:
        raise ValidationError(', '.join(request.errors))
    result = collection_add(context, request, user_info)
    if not result or result['status'] != 'success':
        raise HTTPInternalServerError(explanation='attempt to create account was not successful')
    return result


def _get_first_and_last_names_from_name(name):
    """
    Get user first and last name from name.

        :param name: name object.
    """
    if not name or not name.strip():
        return None, None
    name = name.strip()
    name_split = name.split(' ')
    name_length = len(name_split)
    first_name = name_split[0]
    last_name = name_split[-1] if name_length > 1 else None
    return first_name, last_name


def _get_user_info(user_data):
    """
    get user info from user_data object
        :param user_data: user_data object from oauth service
    """
    if not user_data:
        raise ValidationError('No user data provided')
    if not user_data.get('email') or not user_data.get('email').strip():
        raise ValidationError('No e-mail provided')
    first_name, last_name = _get_first_and_last_names_from_name(user_data.get('name'))
    return {
        'email': user_data['email'],
        'first_name': user_data.get('given_name') or user_data.get('first_name') or first_name,
        'last_name': user_data.get('family_name') or user_data.get('last_name') or last_name or user_data.get('email').split('@')[0],
    }


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

    # create new user account if one does not exist
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
