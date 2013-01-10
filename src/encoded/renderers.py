from pkg_resources import resource_string
from pyramid.threadlocal import get_current_request
import pyramid.renderers
import uuid


class JSON(pyramid.renderers.JSON):
    def dumps(self, value):
        request = get_current_request()
        default = json_renderer._make_default(request)
        return self.serializer(value, default=default, **self.kw)


json_renderer = JSON()


def uuid_adapter(obj, request):
    return str(obj)


json_renderer.add_adapter(uuid.UUID, uuid_adapter)


class PageRenderer:
    def __init__(self, info):
        self.page = resource_string('encoded', 'index.html')

    def __call__(self, value, system):
        # TODO: Include response value in page
        # Return a string to preserve the existing response headers
        return self.page


class PageOrJSON:
    '''Vary response based on accept header or format parameter
    '''
    def __init__(self, info):
        self.json_renderer = json_renderer(info)
        self.page_renderer = PageRenderer(info)

    def __call__(self, value, system):
        request = system.get('request')
        if request is None or request.method != 'GET':
            return self.json_renderer(value, system)

        # Discriminate based on Accept header or format parameter
        format = request.params.get('format')
        if format is None:
            vary = request.response.vary or ()
            request.response.vary = vary + ('Accept',)
            if request.accept == 'application/json':
                format = 'json'
        else:
            format = format.lower()

        if format == 'json':
            return self.json_renderer(value, system)
        else:
            return self.page_renderer(value, system)
