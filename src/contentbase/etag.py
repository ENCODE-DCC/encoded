from pyramid.httpexceptions import HTTPPreconditionFailed
from uuid import UUID


def etag_tid(view_callable):
    def wrapped(context, request):
        result = view_callable(context, request)
        root = request.root
        embedded = (root.get_by_uuid(uuid) for uuid in sorted(request._embedded_uuids))
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
        root = request.root
        mismatching = (
            root.get_by_uuid(uuid).tid != UUID(tid)
            for uuid, tid in uuid_tid)
        if any(mismatching):
            raise HTTPPreconditionFailed("The resource has changed.")
        return view_callable(context, request)

    return wrapped
