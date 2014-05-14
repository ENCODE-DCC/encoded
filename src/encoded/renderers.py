from pkg_resources import resource_filename
from pyramid.events import (
    BeforeRender,
    NewRequest,
    subscriber,
)
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPMovedPermanently,
    HTTPPreconditionFailed,
    HTTPUnauthorized,
    HTTPUnsupportedMediaType,
)
from pyramid.security import authenticated_userid
from pyramid.threadlocal import (
    get_current_request,
    manager,
)
from .validation import CSRFTokenError
from subprocess_middleware.tween import SubprocessTween
from urllib import unquote
import logging
import os
import pyramid.renderers
import pyramid.tweens
import time
import uuid


log = logging.getLogger(__name__)


def includeme(config):
    config.add_renderer(None, json_renderer)
    config.add_renderer('null_renderer', NullRenderer)
    config.add_tween('.renderers.page_or_json', under='.stats.stats_tween_factory')
    config.add_tween('.renderers.es_tween_factory', over=pyramid.tweens.MAIN)
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


def choose_format(request):
    login = None
    expected_user = request.headers.get('X-If-Match-User')
    if expected_user is not None:
        login = authenticated_userid(request)
        if login != 'mailto.' + expected_user:
            detail = 'X-If-Match-User does not match'
            raise HTTPPreconditionFailed(detail)

    if request.method not in ('GET', 'HEAD'):
        request.environ['encoded.format'] = 'json'
        if request.content_type != 'application/json':
            detail = "%s is not 'application/json'" % request.content_type
            raise HTTPUnsupportedMediaType(detail)
        token = request.headers.get('X-CSRF-Token')
        if token is not None:
            # Avoid dirtying the session and adding a Set-Cookie header
            # XXX Should consider if this is a good idea or not and timeouts
            if token == dict.get(request.session, '_csrft_', None):
                return
            raise CSRFTokenError('Incorrect CSRF token')

        if login is None:
            login = authenticated_userid(request)
        if login is not None:
            namespace, userid = login.split('.', 1)
            if namespace != 'mailto':
                return
        if request.authorization is not None:
            raise HTTPUnauthorized()
        raise CSRFTokenError('Missing CSRF token')

    format = request.params.get('format')
    if format is None:
        request.environ['encoded.vary'] = ('Accept', 'Authorization')
        if request.authorization is not None:
            format = 'json'
        else:
            mime_type = request.accept.best_match(['text/html', 'application/json'], 'text/html')
            format = mime_type.split('/', 1)[1]
    else:
        format = format.lower()
        if format not in ('html', 'json'):
            format = 'html'

    request.environ['encoded.format'] = format


@subscriber(BeforeRender)
def vary_canonical_redirect(event):
    request = event['request']
    response = request.response

    vary = request.environ.get('encoded.vary', None)
    if vary is not None:
        original_vary = response.vary or ()
        response.vary = original_vary + vary

    if not (request.method in ('GET', 'HEAD') and
            response.status_int == 200 and
            request.environ.get('encoded.canonical_redirect', True)):
        return

    url = event.rendering_val.get('@id', None)
    if url is None:
        return

    path = url.split('?', 1)[0]
    # resource_path will quote ':' but wsgi path_info is unquoted
    if unquote(str(path)).decode('utf-8') != request.script_name + request.path_info:
        qs = request.query_string
        location = path + ('?' if qs else '') + qs
        raise HTTPMovedPermanently(location=location)


def should_transform(request, response):
    format = request.environ.get('encoded.format', 'json')
    if format == 'json':
        return False

    if response.content_type != 'application/json':
        return False

    response.headers['X-href'] = request.url
    request._transform_start = time.time()
    return True


def render_stats(request, response):
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
    after_transform=render_stats,
    args=['node', resource_filename(__name__, 'static/build/renderer.js')],
    env=node_env,
)


def es_tween_factory(handler, registry):
    from pyramid.renderers import render_to_response
    from pyramid.traversal import (
        split_path_info,
        _join_path_tuple,
    )
    from .indexing import ELASTIC_SEARCH
    es = registry[ELASTIC_SEARCH]

    ignore = {
        '/',
        '/search',
        '/session',
        '/login',
        '/logout',
    }

    def es_tween(request):
        choose_format(request)
        if request.method not in ('GET', 'HEAD'):
            return handler(request)

        if request.params.get('source', '') == 'database':
            return handler(request)

        frame = request.params.get('frame', 'embedded')
        if frame not in ('embedded', 'object',):
            return handler(request)

        # Normalize path
        path =  request.path_info or '/'
        path = _join_path_tuple(('',) + split_path_info(path))

        if path in ignore:
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

        value = source[frame]
        return render_to_response(None, value, request)

    return es_tween
