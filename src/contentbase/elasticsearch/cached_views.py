""" Cached views used when model was pulled from elasticsearch.
"""

from itertools import chain
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config
from .interfaces import ICachedItem


def includeme(config):
    config.scan(__name__)


@view_config(context=ICachedItem, request_method='GET', name='embedded')
def cached_view_embedded(context, request):
    source = context.model.source
    allowed = set(source['principals_allowed']['view'])
    if allowed.isdisjoint(request.effective_principals):
        raise HTTPForbidden()
    return source['embedded']


@view_config(context=ICachedItem, request_method='GET', name='object')
def cached_view_object(context, request):
    source = context.model.source
    allowed = set(source['principals_allowed']['view'])
    if allowed.isdisjoint(request.effective_principals):
        raise HTTPForbidden()
    return source['object']


@view_config(context=ICachedItem, request_method='GET', name='audit')
def cached_view_audit(context, request):
    source = context.model.source
    allowed = set(source['principals_allowed']['audit'])
    if allowed.isdisjoint(request.effective_principals):
        raise HTTPForbidden()
    return {
        '@id': source['object']['@id'],
        'audit': source['audit'],
    }


@view_config(context=ICachedItem, request_method='GET', name='audit-self')
def cached_view_audit_self(context, request):
    source = context.model.source
    allowed = set(source['principals_allowed']['audit'])
    if allowed.isdisjoint(request.effective_principals):
        raise HTTPForbidden()
    path = source['object']['@id']
    return {
        '@id': path,
        'audit': [a for a in chain(*source['audit'].values()) if a['path'] == path],
    }
