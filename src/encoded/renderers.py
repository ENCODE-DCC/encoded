from pkg_resources import resource_string
from pyramid.events import (
    NewRequest,
    subscriber,
)
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import authenticated_userid
from pyramid.threadlocal import (
    get_current_request,
    manager,
)
import pyramid.renderers
import uuid


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


class PageRenderer:
    def __init__(self, info):
        self.page = resource_string('encoded', 'index.html')

    def __call__(self, value, system):
        # TODO: Include response value in page
        # Return a string to preserve the existing response headers
        return self.page


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
            if token == request.session.get('_csrft_', None):
                return
            raise HTTPBadRequest('incorrect CSRF token')
        login = authenticated_userid(request)
        if login is not None:
            namespace, userid = login.split(':', 1)
            if namespace != 'mailto':
                return
        raise HTTPBadRequest('missing CSRF token')

    format = request.params.get('format')
    if format is None:
        request.environ['encoded.vary'] = ('Accept',)
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
        self.page_renderer = PageRenderer(info)

    def __call__(self, value, system):
        request = system.get('request')
        vary = request.environ.get('encoded.vary', None)
        if vary is not None:
            original_vary = request.response.vary or ()
            request.response.vary = original_vary + vary

        format = request.environ.get('encoded.format', 'json')
        if format == 'json':
            return self.json_renderer(value, system)
        else:
            return self.page_renderer(value, system)
