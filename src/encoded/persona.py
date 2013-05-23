from browserid.errors import TrustError
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
from .contentbase import make_subrequest
from .storage import (
    DBSession,
    Key,
)
from .validation import ValidationFailure


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


# in a perfect world these would inherit from Classes shared by api module
def verify_assertion(request):
    """Verifies the assertion in the given request.

    Returns the email of the user if everything is valid, otherwise raises
    a ValidationFailure
    """
    verifier = request.registry['persona.verifier']
    try:
        assertion = request.json['assertion']
    except KeyError:
        msg = 'Missing assertion.'
        raise ValidationFailure('body', ['assertion'], msg)
    try:
        data = verifier.verify(assertion)
    except (ValueError, TrustError) as e:
        msg = 'Invalid assertion: %s (%s)' % (e, type(e).__name__)
        raise ValidationFailure('body', ['assertion'], msg)
    else:
        request.validated = data


# Unfortunately, X-Requested-With is not sufficient.
# http://lists.webappsec.org/pipermail/websecurity_lists.webappsec.org/2011-February/007533.html
# Checking the CSRF token in middleware is easier
@view_config(name='login', physical_path='/', request_method='POST',
             subpath_segments=0, permission=NO_PERMISSION_REQUIRED,
             validators=[verify_assertion])
def login(request):
    """View to check the persona assertion and remember the user"""
    data = request.validated
    email = data['email'].lower()
    session = DBSession()
    model = session.query(Key).get(('user:email', email))
    if model is None:
        raise HTTPForbidden()
    login = 'mailto:' + email
    request.response.headerlist.extend(remember(request, login))
    return data


@view_config(name='logout', physical_path='/',
             subpath_segments=0, permission=NO_PERMISSION_REQUIRED)
def logout(request):
    """View to forget the user"""
    request.response.headers = forget(request)
    if asbool(request.params.get('redirect', True)):
        raise HTTPFound(location=request.resource_path(request.root))
    return {'status': 'okay'}


@view_config(name='session', physical_path='/', request_method='GET',
             subpath_segments=0, permission=NO_PERMISSION_REQUIRED)
def session(context, request):
    """ Give the user a CSRF token
    """
    token = request.session.get_csrf_token()
    login = authenticated_userid(request)
    result = {'csrf_token': token, 'persona': None, 'user_properties': {}}
    if login is None:
        return result

    namespace, userid = login.split(':', 1)
    if namespace != 'mailto':
        raise HTTPForbidden()

    result['persona'] = userid
    subreq = make_subrequest(request, '/current-user')
    subreq.override_renderer = 'null_renderer'
    result['user_properties'] = request.invoke_subrequest(subreq)
    return result
