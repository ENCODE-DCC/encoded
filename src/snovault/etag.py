from pyramid.httpexceptions import (
    HTTPNotModified,
    HTTPPreconditionFailed,
)
from .interfaces import CONNECTION


def etag_tid(view_callable):
    def wrapped(context, request):
        result = view_callable(context, request)
        conn = request.registry[CONNECTION]
        embedded = (conn.get_by_uuid(uuid) for uuid in sorted(request._embedded_uuids))
        uuid_tid = ((item.uuid, item.tid) for item in embedded)
        request.response.etag = '&'.join('%s=%s' % (u, t) for u, t in uuid_tid)
        cache_control = request.response.cache_control
        cache_control.private = True
        cache_control.max_age = 0
        cache_control.must_revalidate = True
        return result

    return wrapped


def if_match_tid(view_callable):
    """ ETag conditional PUT/PATCH support

    Returns 412 Precondition Failed when etag does not match.
    """
    def wrapped(context, request):
        if_match = str(request.if_match)
        if if_match == '*':
            return view_callable(context, request)
        uuid_tid = (v.split('=', 1) for v in if_match.strip('"').split('&'))
        conn = request.registry[CONNECTION]
        mismatching = (
            conn.get_by_uuid(uuid).tid != tid
            for uuid, tid in uuid_tid)
        if any(mismatching):
            raise HTTPPreconditionFailed("The resource has changed.")
        return view_callable(context, request)

    return wrapped


def etag_app_version(view_callable):
    def wrapped(context, request):
        etag = request.registry.settings['snovault.app_version']
        if etag in request.if_none_match:
            raise HTTPNotModified()
        result = view_callable(context, request)
        request.response.etag = etag
        return result

    return wrapped


def etag_app_version_effective_principals(view_callable):
    def wrapped(context, request):
        app_version = request.registry.settings['snovault.app_version']
        etag = app_version + ' ' + ' '.join(sorted(request.effective_principals))
        if etag in request.if_none_match:
            raise HTTPNotModified()
        result = view_callable(context, request)
        request.response.etag = etag
        cache_control = request.response.cache_control
        cache_control.private = True
        cache_control.max_age = 0
        cache_control.must_revalidate = True
        return result

    return wrapped
