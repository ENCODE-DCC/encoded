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
