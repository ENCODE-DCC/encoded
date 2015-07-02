from pyramid.security import (
    Everyone,
    principals_allowed_by_permission,
)
from pyramid.traversal import resource_path
from pyramid.view import view_config
from .resources import Item


def includeme(config):
    config.scan(__name__)


@view_config(context=Item, name='index-data', permission='index', request_method='GET')
def item_index_data(context, request):
    uuid = str(context.uuid)
    properties = context.upgrade_properties()
    links = context.links(properties)
    unique_keys = context.unique_keys(properties)

    principals_allowed = {}
    for permission in ('view', 'edit', 'audit'):
        p = principals_allowed_by_permission(context, permission)
        if p is Everyone:
            p = [Everyone]
        principals_allowed[permission] = sorted(p)

    path = resource_path(context)
    paths = {path}
    collection = context.collection

    if collection.unique_key in unique_keys:
        paths.update(
            resource_path(collection, key)
            for key in unique_keys[collection.unique_key])

    for base in (collection, request.root):
        for key_name in ('accession', 'alias'):
            if key_name not in unique_keys:
                continue
            paths.add(resource_path(base, uuid))
            paths.update(
                resource_path(base, key)
                for key in unique_keys[key_name])

    path = path + '/'
    embedded = request.embed(path, '@@embedded')
    object = request.embed(path, '@@object')
    audit = request.embed(path, '@@audit')['audit']

    document = {
        'audit': audit,
        'embedded': embedded,
        'embedded_uuids': sorted(request._embedded_uuids),
        'item_type': context.item_type,
        'linked_uuids': sorted(request._linked_uuids),
        'links': links,
        'object': object,
        'paths': sorted(paths),
        'principals_allowed': principals_allowed,
        'properties': properties,
        'propsheets': {
            name: context.propsheets[name]
            for name in context.propsheets.keys() if name != ''
        },
        'tid': context.tid,
        'unique_keys': unique_keys,
        'uuid': uuid,
    }

    return document
