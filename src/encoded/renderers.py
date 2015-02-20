from pkg_resources import resource_filename
from pyramid.events import (
    BeforeRender,
    subscriber,
)
from pyramid.httpexceptions import (
    HTTPMovedPermanently,
    HTTPPreconditionFailed,
    HTTPUnauthorized,
    HTTPUnsupportedMediaType,
)
from pyramid.security import forget
from pyramid.settings import asbool
from pyramid.threadlocal import (
    get_current_request,
    manager,
)
from pyramid.traversal import (
    split_path_info,
    _join_path_tuple,
)

from .validation import CSRFTokenError
from subprocess_middleware.tween import SubprocessTween
import json
import logging
import os
import psutil
import pyramid.renderers
import time
import uuid


log = logging.getLogger(__name__)


def includeme(config):
    config.add_renderer(None, json_renderer)
    config.add_renderer('null_renderer', NullRenderer)
    config.add_tween('.renderers.fix_request_method_tween_factory', under=pyramid.tweens.INGRESS)
    config.add_tween(
        '.stats.stats_tween_factory', under='.renderers.fix_request_method_tween_factory')
    config.add_tween(
        '.renderers.normalize_cookie_tween_factory', under='.stats.stats_tween_factory')
    config.add_tween('.renderers.page_or_json', under='.renderers.normalize_cookie_tween_factory')
    config.add_tween('.renderers.security_tween_factory', under='pyramid_tm.tm_tween_factory')
    config.scan(__name__)


class JSON(pyramid.renderers.JSON):
    '''Provide easier access to the configured serializer
    '''
    def dumps(self, value):
        request = get_current_request()
        default = self._make_default(request)
        return json.dumps(value, default=default, **self.kw)


class BinaryFromJSON:
    def __init__(self, app_iter):
        self.app_iter = app_iter

    def __len__(self):
        return len(self.app_iter)

    def __iter__(self):
        for s in self.app_iter:
            yield s.encode('utf-8')


class JSONResult(object):
    def __init__(self):
        self.app_iter = []
        self.write = self.app_iter.append

    @classmethod
    def serializer(cls, value, **kw):
        fp = cls()
        json.dump(value, fp, **kw)
        if str is bytes:
            return fp.app_iter
        else:
            return BinaryFromJSON(fp.app_iter)


json_renderer = JSON(serializer=JSONResult.serializer)


def uuid_adapter(obj, request):
    return str(obj)


def listy_adapter(obj, request):
    return list(obj)


json_renderer.add_adapter(uuid.UUID, uuid_adapter)
json_renderer.add_adapter(set, listy_adapter)
json_renderer.add_adapter(frozenset, listy_adapter)


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


def fix_request_method_tween_factory(handler, registry):
    """ Fix Request method changed by mod_wsgi.

    See: https://github.com/GrahamDumpleton/mod_wsgi/issues/2

    Apache config:
        SetEnvIf Request_Method HEAD X_REQUEST_METHOD=HEAD
    """

    def fix_request_method_tween(request):
        environ = request.environ
        if 'X_REQUEST_METHOD' in environ:
            environ['REQUEST_METHOD'] = environ['X_REQUEST_METHOD']
        return handler(request)

    return fix_request_method_tween


def security_tween_factory(handler, registry):

    def security_tween(request):
        login = None
        expected_user = request.headers.get('X-If-Match-User')
        if expected_user is not None:
            login = request.authenticated_userid
            if login != 'mailto.' + expected_user:
                detail = 'X-If-Match-User does not match'
                raise HTTPPreconditionFailed(detail)

        # wget may only send credentials following a challenge response.
        auth_challenge = asbool(request.headers.get('X-Auth-Challenge', False))
        if auth_challenge or request.authorization is not None:
            login = request.authenticated_userid
            if login is None:
                raise HTTPUnauthorized(headerlist=forget(request))

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
            login = request.authenticated_userid
        if login is not None:
            namespace, userid = login.split('.', 1)
            if namespace not in ('mailto', 'persona'):
                return handler(request)
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

    if '/@@' in request.path_info:
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


# Rendering huge pages can make the node process memory usage explode.
# Ideally we would let the OS handle this with `ulimit` or by calling
# `resource.setrlimit()` from  a `subprocess.Popen(preexec_fn=...)`.
# Unfortunately Linux does not enforce RLIMIT_RSS.
# An alternative would be to use cgroups, but that makes per-process limits
# tricky to enforce (we would need to create one cgroup per process.)
# So we just manually check the resource usage after each transform.

rss_limit = 256 * (1024 ** 2)  # MB


def reload_process(process):
    return psutil.Process(process.pid).memory_info().rss > rss_limit

node_env = os.environ.copy()
node_env['NODE_PATH'] = ''

page_or_json = SubprocessTween(
    should_transform=should_transform,
    after_transform=after_transform,
    reload_process=reload_process,
    args=['node', resource_filename(__name__, 'static/build/renderer.js')],
    env=node_env,
)
