from past.builtins import basestring
from pyramid.threadlocal import manager as threadlocal_manager


def get_root_request():
    if threadlocal_manager.stack:
        return threadlocal_manager.stack[0]['request']


def ensurelist(value):
    if isinstance(value, basestring):
        return [value]
    return value


def simple_path_ids(obj, path):
    if isinstance(path, basestring):
        path = path.split('.')
    if not path:
        yield obj
        return
    name = path[0]
    remaining = path[1:]
    value = obj.get(name, None)
    if value is None:
        return
    if isinstance(value, list):
        for member in value:
            for result in simple_path_ids(member, remaining):
                yield result
    else:
        for result in simple_path_ids(value, remaining):
            yield result
