from browserid.errors import TrustError
from contentbase.validation import ValidationFailure
from contentbase.validators import no_validate_item_content_post
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.config import ConfigurationError
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
from pyramid.view import (
    view_config,
)


_marker = object()


AUDIENCES_MESSAGE = """\
Missing persona.audiences settings. This is needed for security reasons. \
See https://developer.mozilla.org/en-US/docs/Mozilla/Persona/Security_Considerations \
for details."""


def includeme(config):
    config.scan(__name__)
    settings = config.registry.settings

    if 'persona.audiences' not in settings:
        raise ConfigurationError(AUDIENCES_MESSAGE)
    # Construct a browserid Verifier using the configured audience.
    # This will pre-compile some regexes to reduce per-request overhead.
    verifier_factory = config.maybe_dotted(settings.get('persona.verifier',
                                                        'browserid.RemoteVerifier'))
    audiences = aslist(settings['persona.audiences'])
    config.registry['persona.verifier'] = verifier_factory(audiences)
    config.add_route('login', 'login')
    config.add_route('logout', 'logout')
    config.add_route('session', 'session')
    config.add_route('impersonate-user', 'impersonate-user')


class LoginDenied(HTTPForbidden):
    title = 'Login failure'


class PersonaAuthenticationPolicy(CallbackAuthenticationPolicy):
    """
    Checks assertion during authentication so login can construct user session.
    """
    login_path = '/login'
    method = 'POST'

    def unauthenticated_userid(self, request):
        if request.method != self.method or request.path != self.login_path:
            return None

        cached = getattr(request, '_persona_authenticated', _marker)
        if cached is not _marker:
            return cached

        verifier = request.registry['persona.verifier']
        try:
            assertion = request.json['assertion']
        except (ValueError, TypeError, KeyError):
            if self.debug:
                self._log(
                    'Missing assertion.',
                    'unauthenticated_userid',
                    request)
            request._persona_authenticated = None
            return None
        try:
            data = verifier.verify(assertion)
        except (ValueError, TrustError) as e:
            if self.debug:
                self._log(
                    ('Invalid assertion: %s (%s)', (e, type(e).__name__)),
                    'unauthenticated_userid',
                    request)
            request._persona_authenticated = None
            return None

        email = request._persona_authenticated = data['email'].lower()
        return email

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
    """View to check the persona assertion and remember the user"""
    login = request.authenticated_userid
    if login is None:
        namespace = userid = None
    else:
        namespace, userid = login.split('.', 1)
    if namespace != 'persona':
        request.session['user_properties'] = {}
        request.response.headerlist.extend(forget(request))
        raise LoginDenied()
    request.session['user_properties'] = request.embed('/current-user', as_user=userid)
    request.response.headerlist.extend(remember(request, 'mailto.' + userid))
    return request.session


@view_config(route_name='logout',
             permission=NO_PERMISSION_REQUIRED, http_cache=0)
def logout(request):
    """View to forget the user"""
    request.session.get_csrf_token()
    request.session.invalidate()
    request.response.headerlist.extend(forget(request))
    if asbool(request.params.get('redirect', True)):
        raise HTTPFound(location=request.resource_path(request.root))
    return request.session


@view_config(route_name='session', request_method='GET',
             permission=NO_PERMISSION_REQUIRED)
def session(request):
    """ Possibly refresh the user's session cookie
    """
    request.session.get_csrf_token()
    if not request.params.get('reload'):
        return request.session
    # Reload the user's session cookie
    login = request.authenticated_userid
    if login is None:
        namespace = userid = None
    else:
        namespace, userid = login.split('.', 1)
    if namespace != 'mailto':
        return request.session
    request.session['user_properties'] = request.embed('/current-user', as_user=userid)
    return request.session


@view_config(route_name='impersonate-user', request_method='GET', permission='impersonate')
def impersonate_user_form(request):
    return {
        '@type': ['impersonate-user-form', 'form']
    }


@view_config(route_name='impersonate-user', request_method='POST',
             validators=[no_validate_item_content_post],
             permission='impersonate')
def impersonate_user(request):
    """As an admin, impersonate a different user."""
    request.session.get_csrf_token()
    userid = request.validated['userid']
    user = request.embed('/current-user', as_user=userid)
    if not user:
        raise ValidationFailure('body', ['userid'], 'User not found.')
    request.session['user_properties'] = user
    request.session['disable_persona'] = True
    request.response.headerlist.extend(remember(request, 'mailto.' + userid))
    return {'@graph': [request.embed('/current-user', as_user=userid)]}
