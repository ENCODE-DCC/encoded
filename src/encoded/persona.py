from browserid.errors import TrustError
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.config import ConfigurationError
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound,
)
from pyramid.security import (
    NO_PERMISSION_REQUIRED,
    authenticated_userid,
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
from .renderers import make_subrequest

_marker = object()


AUDIENCES_MESSAGE = """\
Missing persona.audiences settings. This is needed for security reasons. \
See https://developer.mozilla.org/en-US/docs/Mozilla/Persona/Security_Considerations \
for details."""


def includeme(config):
    config.scan(__name__)
    settings = config.registry.settings

    if not 'persona.audiences' in settings:
        raise ConfigurationError(AUDIENCES_MESSAGE)
    # Construct a browserid Verifier using the configured audience.
    # This will pre-compile some regexes to reduce per-request overhead.
    verifier_factory = config.maybe_dotted(settings.get('persona.verifier',
                                                        'browserid.RemoteVerifier'))
    audiences = aslist(settings['persona.audiences'])
    config.registry['persona.verifier'] = verifier_factory(audiences)


class LoginDenied(HTTPForbidden):
    title = 'Login failure'


class PersonaAuthenticationPolicy(CallbackAuthenticationPolicy):
    """
    Checks assertion during authentication so login can construct user session.
    """
    view_name = 'login'
    method = 'POST'

    def unauthenticated_userid(self, request):
        if request.method != self.method or \
                getattr(request, 'view_name', None) != self.view_name:
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
@view_config(name='login', physical_path='/', request_method='POST',
             subpath_segments=0, permission=NO_PERMISSION_REQUIRED)
def login(request):
    """View to check the persona assertion and remember the user"""
    login = authenticated_userid(request)
    if login is None:
        namespace = userid = None
    else:
        namespace, userid = login.split('.', 1)
    if namespace != 'persona':
        request.session['user_properties'] = {}
        request.response.headerlist.extend(forget(request))
        raise LoginDenied()
    subreq = make_subrequest(request, '/current-user')
    subreq.remote_user = userid
    subreq.override_renderer = 'null_renderer'
    request.session['user_properties'] = request.invoke_subrequest(subreq)
    request.response.headerlist.extend(remember(request, 'mailto.' + userid))
    return request.session


@view_config(name='logout', physical_path='/',
             subpath_segments=0, permission=NO_PERMISSION_REQUIRED, http_cache=0)
def logout(request):
    """View to forget the user"""
    request.session.get_csrf_token()
    request.session['user_properties'] = {}
    request.response.headerlist.extend(forget(request))
    if asbool(request.params.get('redirect', True)):
        raise HTTPFound(location=request.resource_path(request.root))
    return request.session


@view_config(name='session', physical_path='/', request_method='GET',
             subpath_segments=0, permission=NO_PERMISSION_REQUIRED)
def session(context, request):
    """ Possibly refresh the user's session cookie
    """
    request.session.get_csrf_token()
    if not request.params.get('reload'):
        return request.session
    # Reload the user's session cookie
    login = authenticated_userid(request)
    if login is None:
        namespace = userid = None
    else:
        namespace, userid = login.split('.', 1)
    if namespace != 'mailto':
        return request.session
    subreq = make_subrequest(request, '/current-user')
    subreq.remote_user = userid
    subreq.override_renderer = 'null_renderer'
    request.session['user_properties'] = request.invoke_subrequest(subreq)
    return request.session
