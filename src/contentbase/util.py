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
    if not isinstance(value, list):
        value = [value]
    for member in value:
        for result in simple_path_ids(member, remaining):
            yield result


def expand_path(request, obj, path):
    if isinstance(path, basestring):
        path = path.split('.')
    if not path:
        return
    name = path[0]
    remaining = path[1:]
    value = obj.get(name, None)
    if value is None:
        return
    if isinstance(value, list):
        for index, member in enumerate(value):
            if not isinstance(member, dict):
                member = value[index] = request.embed(member, '@@object')
            expand_path(request, member, remaining)
    else:
        if not isinstance(value, dict):
            value = obj[name] = request.embed(value, '@@object')
        expand_path(request, value, remaining)
