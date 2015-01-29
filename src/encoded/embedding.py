from copy import deepcopy
from .cache import ManagerLRUCache
from past.builtins import basestring
from posixpath import join
from pyramid.compat import (
    native_,
    unquote_bytes_to_wsgi,
)
from pyramid.httpexceptions import HTTPNotFound


def includeme(config):
    config.scan(__name__)
    config.add_request_method(embed, 'embed')
    config.add_request_method(lambda request: set(), '_embedded_uuids', reify=True)
    config.add_request_method(lambda request: set(), '_linked_uuids', reify=True)


def make_subrequest(request, path):
    """ Make a subrequest

    Copies request environ data for authentication.

    May be better to just pull out the resource through traversal and manually
    perform security checks.
    """
    env = request.environ.copy()
    if path and '?' in path:
        path_info, query_string = path.split('?', 1)
        path_info = path_info
    else:
        path_info = path
        query_string = ''
    env['PATH_INFO'] = path_info
    env['QUERY_STRING'] = query_string
    subreq = request.__class__(env, method='GET', content_type=None,
                               body=b'')
    subreq.remove_conditional_headers()
    # XXX "This does not remove headers like If-Match"
    subreq.__parent__ = request
    return subreq


embed_cache = ManagerLRUCache('embed_cache')


def embed(request, *elements, **kw):
    """ as_user=True for current user
    """
    # Should really be more careful about what gets included instead.
    # Cache cut response time from ~800ms to ~420ms.
    as_user = kw.get('as_user')
    path = join(*elements)
    path = unquote_bytes_to_wsgi(native_(path))
    if as_user is not None:
        result, embedded, linked = _embed(request, path, as_user)
    else:
        cached = embed_cache.get(path, None)
        if cached is None:
            cached = _embed(request, path)
            embed_cache[path] = cached
        result, embedded, linked = cached
        result = deepcopy(result)
    request._embedded_uuids.update(embedded)
    request._linked_uuids.update(linked)
    return result


def _embed(request, path, as_user='EMBED'):
    subreq = make_subrequest(request, path)
    subreq.override_renderer = 'null_renderer'
    if as_user is not True:
        if 'HTTP_COOKIE' in subreq.environ:
            del subreq.environ['HTTP_COOKIE']
        subreq.remote_user = as_user
    try:
        result = request.invoke_subrequest(subreq)
    except HTTPNotFound:
        raise KeyError(path)
    return result, subreq._embedded_uuids, subreq._linked_uuids


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
