import warnings
import json
from pyramid.settings import aslist
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.config import ConfigurationError
from pyramid.security import remember, forget

from sqlalchemy.orm.exc import NoResultFound
from .storage import (
    DBSession,
    CurrentStatement,
    Resource,
    UserMap
    )
import logging
import browserid.errors


logger = logging.getLogger(__name__)


def includeme(config):

    settings = config.get_settings()
    secret_key = settings.get('persona.secret', None)
    # Default authentication and authorization policies. Those are needed to remember the userid.
    authn_policy = AuthTktAuthenticationPolicy(secret_key, hashalg='sha512', callback=groupfinder)
    config.set_authentication_policy(authn_policy)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    if 'persona.audience' in settings:
        settings['persona.audiences'] = settings['persona.audience']
        warnings.warn('persona.audience has been changed to persona.audiences, and may accept more than one value. '
                      'Please update you config file accordingly.', stacklevel=3)

    if not 'persona.audiences' in settings:
        raise ConfigurationError('Missing persona.audience settings. This is needed for security reasons. '
                                 'See https://developer.mozilla.org/en-US/docs/Persona/Security_Considerations for details.')
    # Construct a browserid Verifier using the configured audience.
    # This will pre-compile some regexes to reduce per-request overhead.
    verifier_factory = config.maybe_dotted(settings.get('persona.verifier',
                                                        'browserid.RemoteVerifier'))
    audiences = aslist(settings['persona.audiences'])
    config.registry['persona.verifier'] = verifier_factory(audiences)

    # Parameters for the request API call
    request_params = {}
    for option in ('privacyPolicy', 'siteLogo', 'siteName', 'termsOfService'):
        setting_name = 'persona.%s' % option
        if setting_name in settings:
            request_params[option] = settings[setting_name]
    config.registry['persona.request_params'] = json.dumps(request_params)

    # Login and logout views - these could be moved to authz.py and imported
    # via config.include('.authz') instead

    login_route = settings.get('persona.login_route', 'login')
    config.registry['persona.login_route'] = login_route
    login_path = settings.get('persona.login_path', '/login')
    config.add_route(login_route, login_path)
    config.add_view(login, route_name=login_route,
                    permission=NO_PERMISSION_REQUIRED)

    logout_route = settings.get('persona.logout_route', 'logout')
    config.registry['persona.logout_route'] = logout_route
    logout_path = settings.get('persona.logout_path', '/logout')
    config.add_route(logout_route, logout_path)
    config.add_view(logout, route_name=logout_route,
                    permission=NO_PERMISSION_REQUIRED)


def verify_login(request):
    """Verifies the assertion and the csrf token in the given request.

    Returns the email of the user if everything is valid, otherwise raises
    a HTTPBadRequest"""
    verifier = request.registry['persona.verifier']
    try:
        ##data = verifier.verify(request.POST['assertion'])
        data = verifier.verify(request.json_body['assertion'])
    except KeyError as e:
        logger.info('verify_login called wtih no assertion: %s', e)
        raise HTTPBadRequest('No assertion: (req: %s)' % request.json_body)
    except (ValueError, browserid.errors.TrustError) as e:
        logger.info('Failed persona login: %s (%s)', e, type(e).__name__)
        raise HTTPBadRequest('Invalid assertion: %s (%s)' % (e, type(e).__name__))
    return data


def login(request):
    """View to check the persona assertion and remember the user"""
    try:
        from_url = request.json_body['came_from']
    except KeyError as e:
        logger.info('/login has no came_from post: %s', e)
    data = verify_login(request)
    request.response.content_type = 'application/json'
    request.response.headers = remember(request, data['email'])
    return data


def logout(request):
    """View to forget the user"""
    try:
        from_url = request.json_body['came_from']
    except KeyError as e:
        logger.info('/logout has no came_from post: %s', e)
    request.response.content_type = 'application/json'
    request.response.headers = forget(request)
    return {'email': None}


class RootFactory(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


def groupfinder(userid, request):
    session = DBSession()
    query = session.query(UserMap).filter(UserMap.persona_email == userid)
    try:
        query.one()
        return ['g:admin']  # return ['g:%s' % g for g in user.groups]
    except NoResultFound:
        return None
