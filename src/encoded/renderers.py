from .json_script_escape import json_script_escape
from pkg_resources import resource_filename
from pyramid.events import (
    NewRequest,
    subscriber,
)
from pyramid.decorator import reify
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
    HTTPMovedPermanently,
)
from pyramid.security import authenticated_userid
from pyramid.threadlocal import (
    get_current_request,
    manager,
)
import json
import os
import pyramid.renderers
import subprocess
import threading
import time
import uuid


def includeme(config):
    config.add_renderer(None, PageOrJSON)
    config.add_renderer('null_renderer', NullRenderer)
    config.scan(__name__)


class JSON(pyramid.renderers.JSON):
    '''Provide easier access to the configured serializer
    '''
    def dumps(self, value):
        request = get_current_request()
        default = json_renderer._make_default(request)
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


class PageWorker(threading.local):
    """ We only want one of these per thread
    """
    process_args = [
        'node',
        resource_filename(__name__, 'static/build/renderer.js'),
    ]

    @reify
    def process(self):
        """ defer creation as __init__ also called in management thread
        """
        node_env = os.environ.copy()
        node_env['NODE_PATH']= ''
        return subprocess.Popen(
            self.process_args, close_fds=True,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=node_env,
        )

    def render(self, value, system):
        request = system['request']
        request.response.content_type = 'text/html'
        data = '{"href":%s,"context":%s}\0' % (json.dumps(request.url), value)

        start = int(time.time() * 1e6)
        self.process.stdin.write(data)
        header = self.process.stdout.readline()
        result_type, content_length = header.split(' ', 1)
        content_length = int(content_length)
        output = []
        pos = 0

        while pos < content_length:
            out = self.process.stdout.read(content_length - pos)
            pos += len(out)
            output.append(out)

        end = int(time.time() * 1e6)

        stats = request._stats
        stats['render_count'] = stats.get('render_count', 0) + 1
        duration = end - start
        stats['render_time'] = stats.get('render_time', 0) + duration

        result = ''.join(output)
        if result_type == 'RESULT':
            return result
        else:
            raise HTTPInternalServerError(result)

    def __call__(self, info):
        """ Called per view
        """
        def _render(value, system):
            return self.render(value, system)

        return _render


page_renderer = PageWorker()


class CSRFTokenError(HTTPBadRequest):
    pass


@subscriber(NewRequest)
def choose_format(event):
    # Ignore subrequests
    if len(manager.stack) > 1:
        return

    # Discriminate based on Accept header or format parameter
    request = event.request
    if request.method not in ('GET', 'HEAD'):
        request.environ['encoded.format'] = 'json'
        token = request.headers.get('X-CSRF-Token')
        if token is not None:
            # Avoid dirtying the session and adding a Set-Cookie header
            # XXX Should consider if this is a good idea or not and timeouts
            if token == dict.get(request.session, '_csrft_', None):
                return
            raise CSRFTokenError('Incorrect CSRF token')
        login = authenticated_userid(request)
        if login is not None:
            namespace, userid = login.split('.', 1)
            if namespace != 'mailto':
                return
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


class PageOrJSON:
    '''Vary response based on accept header or format parameter
    '''
    def __init__(self, info):
        self.json_renderer = json_renderer(info)
        self.page_renderer = page_renderer(info)

    def __call__(self, value, system):
        request = system.get('request')
        vary = request.environ.get('encoded.vary', None)
        if vary is not None:
            original_vary = request.response.vary or ()
            request.response.vary = original_vary + vary

        if (request.method in ('GET', 'HEAD') and
                request.response.status_int == 200 and
                isinstance(value, dict) and
                request.environ.get('encoded.canonical_redirect', True)):
            url = value.get('@id', None)
            if url is not None:
                path = url.split('?', 1)[0]
                if path != request.path:
                    qs = request.query_string
                    location = path + ('?' if qs else '') + qs
                    raise HTTPMovedPermanently(location=location)

        format = request.environ.get('encoded.format', 'json')
        value = self.json_renderer(value, system)
        if format == 'json':
            return value
        else:
            return self.page_renderer(value, system)
