from copy import deepcopy
from urllib import unquote
from .cache import ManagerLRUCache
from pyramid.httpexceptions import HTTPNotFound


def make_subrequest(request, path):
    """ Make a subrequest

    Copies request environ data for authentication.

    May be better to just pull out the resource through traversal and manually
    perform security checks.
    """
    env = request.environ.copy()
    if path and '?' in path:
        path_info, query_string = path.split('?', 1)
        path_info = unquote(path_info)
    else:
        path_info = unquote(path)
        query_string = ''
    env['PATH_INFO'] = path_info
    env['QUERY_STRING'] = query_string
    subreq = request.__class__(env, method='GET', content_type=None,
                               body=b'')
    subreq.remove_conditional_headers()
    # XXX "This does not remove headers like If-Match"
    return subreq


embed_cache = ManagerLRUCache('embed_cache')


def embed(request, path, as_user=None):
    """ as_user=True for current user
    """
    # Should really be more careful about what gets included instead.
    # Cache cut response time from ~800ms to ~420ms.
    if as_user is not None:
        return _embed(request, path, as_user)
    result = embed_cache.get(path, None)
    if result is None:
        result = _embed(request, path)
        embed_cache[path] = result
    return deepcopy(result)


def _embed(request, path, as_user='EMBED'):
    subreq = make_subrequest(request, path)
    subreq.override_renderer = 'null_renderer'
    if as_user is not True:
        if 'HTTP_COOKIE' in subreq.environ:
            del subreq.environ['HTTP_COOKIE']
        subreq.remote_user = as_user
    try:
        return request.invoke_subrequest(subreq)
    except HTTPNotFound:
        raise KeyError(path)
