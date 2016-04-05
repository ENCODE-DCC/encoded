from pyramid.threadlocal import get_current_request
import json
import pyramid.renderers
import uuid


def includeme(config):
    config.add_renderer(None, json_renderer)


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
