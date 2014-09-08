from copy import deepcopy
from pkg_resources import resource_filename
from pyramid.events import (
    BeforeRender,
    subscriber,
)
from pyramid.interfaces import IRootFactory
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPMovedPermanently,
    HTTPNotFound,
    HTTPPreconditionFailed,
    HTTPUnauthorized,
    HTTPUnsupportedMediaType,
)
from pyramid.renderers import render_to_response
from pyramid.security import authenticated_userid
from pyramid.threadlocal import (
    get_current_request,
    manager,
)
from pyramid.traversal import (
    split_path_info,
    _join_path_tuple,
)
from urllib import unquote
from .cache import ManagerLRUCache
from .validation import CSRFTokenError
from subprocess_middleware.tween import SubprocessTween
import logging
import os
import pyramid.renderers
import time
import uuid


log = logging.getLogger(__name__)


def includeme(config):
    config.add_renderer(None, json_renderer)
    config.add_renderer('null_renderer', NullRenderer)
    config.add_tween(
        '.renderers.normalize_cookie_tween_factory', under='.stats.stats_tween_factory')
    config.add_tween('.renderers.page_or_json', under='.renderers.normalize_cookie_tween_factory')
    config.add_tween('.renderers.security_tween_factory', under='pyramid_tm.tm_tween_factory')
    config.add_tween('.renderers.es_tween_factory', under='.renderers.security_tween_factory')
    config.scan(__name__)


class JSON(pyramid.renderers.JSON):
    '''Provide easier access to the configured serializer
    '''
    def dumps(self, value):
        request = get_current_request()
        default = self._make_default(request)
        return self.serializer(value, default=default, **self.kw)


json_renderer = JSON()


def uuid_adapter(obj, request):
    return str(obj)


json_renderer.add_adapter(uuid.UUID, uuid_adapter)


class NullRenderer:
    '''Sets result value directly as response.
    '''
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        if request is None:
            return value
        request.response = value
        return None


def make_subrequest(request, path):
    """ Make a subrequest

    Copies request environ data for authentication.

    May be better to just pull out the resource through traversal and manually
    perform security checks.
    """
    env = request.environ.copy()
    if path and '?' in path:
        path_info, query_string = path.split('?', 1)
        path_info = unquote(path_info)
    else:
        path_info = unquote(path)
        query_string = ''
    env['PATH_INFO'] = path_info
    env['QUERY_STRING'] = query_string
    subreq = request.__class__(env, method='GET', content_type=None,
                               body=b'')
    subreq.remove_conditional_headers()
    # XXX "This does not remove headers like If-Match"
    return subreq


embed_cache = ManagerLRUCache('embed_cache')


def embed(request, path, as_user=False):
    # Should really be more careful about what gets included instead.
    # Cache cut response time from ~800ms to ~420ms.
    if as_user:
        return _embed(request, path, as_user)
    result = embed_cache.get(path, None)
    if result is not None:
        return deepcopy(result)
    result = _embed(request, path, as_user)
    if not as_user:
        embed_cache[path] = deepcopy(result)
    return result


def _embed(request, path, as_user=False):
    subreq = make_subrequest(request, path)
    subreq.override_renderer = 'null_renderer'
    if not as_user:
        if 'HTTP_COOKIE' in subreq.environ:
            del subreq.environ['HTTP_COOKIE']
        subreq.remote_user = 'EMBED'
    try:
        return request.invoke_subrequest(subreq)
    except HTTPNotFound:
        raise KeyError(path)


def maybe_include_embedded(request, result):
    if len(manager.stack) != 1:
        return
    embedded = manager.stack[0].get('encoded_embedded', None)
    if embedded:
        result['_embedded'] = {'resources': embedded}


def security_tween_factory(handler, registry):

    def security_tween(request):
        login = None
        expected_user = request.headers.get('X-If-Match-User')
        if expected_user is not None:
            login = authenticated_userid(request)
            if login != 'mailto.' + expected_user:
                detail = 'X-If-Match-User does not match'
                raise HTTPPreconditionFailed(detail)

        if request.method in ('GET', 'HEAD'):
            return handler(request)

        if request.content_type != 'application/json':
            detail = "%s is not 'application/json'" % request.content_type
            raise HTTPUnsupportedMediaType(detail)

        token = request.headers.get('X-CSRF-Token')
        if token is not None:
            # Avoid dirtying the session and adding a Set-Cookie header
            # XXX Should consider if this is a good idea or not and timeouts
            if token == dict.get(request.session, '_csrft_', None):
                return handler(request)
            raise CSRFTokenError('Incorrect CSRF token')

        if login is None:
            login = authenticated_userid(request)
        if login is not None:
            namespace, userid = login.split('.', 1)
            if namespace != 'mailto':
                return handler(request)
        if request.authorization is not None:
            raise HTTPUnauthorized()
        raise CSRFTokenError('Missing CSRF token')

    return security_tween


def normalize_cookie_tween_factory(handler, registry):
    from webob.cookies import Cookie

    ignore = {
        '/favicon.ico',
    }

    def normalize_cookie_tween(request):
        if request.path in ignore or request.path.startswith('/static/'):
            return handler(request)

        session = request.session
        if session or session._cookie_name not in request.cookies:
            return handler(request)

        response = handler(request)
        existing = response.headers.getall('Set-Cookie')
        if existing:
            cookies = Cookie()
            for header in existing:
                cookies.load(header)
            if session._cookie_name in cookies:
                return response

        response.delete_cookie(
            session._cookie_name,
            path=session._cookie_path,
            domain=session._cookie_domain,
        )

        return response

    return normalize_cookie_tween


@subscriber(BeforeRender)
def canonical_redirect(event):
    request = event['request']

    # Ignore subrequests
    if len(manager.stack) > 1:
        return

    if request.method not in ('GET', 'HEAD'):
        return
    if request.response.status_int != 200:
        return
    if not request.environ.get('encoded.canonical_redirect', True):
        return
    if request.path_info == '/':
        return

    canonical_path = event.rendering_val.get('@id', None)
    if canonical_path is None:
        return
    canonical_path = canonical_path.split('?', 1)[0]

    request_path = _join_path_tuple(('',) + split_path_info(request.path_info))
    if (request_path == canonical_path.rstrip('/') and
            request.path_info.endswith('/') == canonical_path.endswith('/')):
        return

    qs = request.query_string
    location = canonical_path + ('?' if qs else '') + qs
    raise HTTPMovedPermanently(location=location)


def should_transform(request, response):
    if request.method not in ('GET', 'HEAD'):
        return False

    if response.content_type != 'application/json':
        return False

    format = request.params.get('format')
    if format is None:
        original_vary = response.vary or ()
        response.vary = original_vary + ('Accept', 'Authorization')
        if request.authorization is not None:
            format = 'json'
        else:
            mime_type = request.accept.best_match(
                [
                    'text/html',
                    'application/ld+json',
                    'application/json',
                ],
                'text/html')
            format = mime_type.split('/', 1)[1]
            if format == 'ld+json':
                format = 'json'
    else:
        format = format.lower()
        if format not in ('html', 'json'):
            format = 'html'

    if format == 'json':
        return False

    response.headers['X-href'] = request.url
    request._transform_start = time.time()
    return True


def after_transform(request, response):
    end = time.time()
    duration = int((end - request._transform_start) * 1e6)
    stats = request._stats
    stats['render_count'] = stats.get('render_count', 0) + 1
    stats['render_time'] = stats.get('render_time', 0) + duration
    request._stats_html_attribute = True


node_env = os.environ.copy()
node_env['NODE_PATH'] = ''

page_or_json = SubprocessTween(
    should_transform=should_transform,
    after_transform=after_transform,
    args=['node', resource_filename(__name__, 'static/build/renderer.js')],
    env=node_env,
)


def es_tween_factory(handler, registry):
    from .indexing import ELASTIC_SEARCH
    es = registry.get(ELASTIC_SEARCH)
    if es is None:
        return handler

    default_datastore = registry.settings.get('item_datastore', 'database')

    ignore = {
        '/',
        '/favicon.ico',
        '/search',
        '/session',
        '/login',
        '/logout',
    }

    def es_tween(request):
        if request.method not in ('GET', 'HEAD'):
            return handler(request)

        if request.params.get('datastore', default_datastore) != 'elasticsearch':
            return handler(request)

        frame = request.params.get('frame', 'page')
        if frame not in ('object', 'embedded', 'page',):
            return handler(request)

        # Normalize path
        path_tuple = split_path_info(request.path_info)
        path = _join_path_tuple(('',) + path_tuple)

        if path in ignore or path.startswith('/static/'):
            return handler(request)

        query = {'query': {'term': {'paths': path}}}
        data = es.search(index='encoded', body=query)
        hits = data['hits']['hits']
        if len(hits) != 1:
            return handler(request)

        source = hits[0]['_source']
        allowed = set(source['principals_allowed_view'])
        if allowed.isdisjoint(request.effective_principals):
            raise HTTPForbidden()

        if frame == 'page':
            properties = source['embedded']
            request.root = registry.getUtility(IRootFactory)(request)
            collection = request.root.get(properties['@type'][0])
            rendering_val = collection.Item.expand_page(request, properties)

            # Add actions
            allowed = set(source['principals_allowed_edit'])
            if allowed.intersection(request.effective_principals):
                rendering_val['actions'] = collection.Item.actions

            # Add default page
            default_page_path = None
            if len(path_tuple) == 0:
                default_page_path = '/pages/homepage/'
            elif len(path_tuple) == 1:
                default_page_path = '/pages' + path
            if default_page_path:
                try:
                    default_page = embed(request, default_page_path)
                except KeyError:
                    pass
                else:
                    if default_page:
                        rendering_val['default_page'] = default_page

        else:
            rendering_val = source[frame]
        return render_to_response(None, rendering_val, request)

    return es_tween
