from collections import OrderedDict
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from .etag import etag_app_version_effective_principals
from .interfaces import (
    COLLECTIONS,
    TYPES,
)


def includeme(config):
    config.add_route('schemas', '/profiles/')
    config.add_route('schema', '/profiles/{type_name}.json')
    config.scan(__name__)


def _annotated_schema(type_info, request):
    schema = type_info.schema.copy()
    schema['@type'] = ['JSONSchema']
    if type_info.factory is None:
        return schema

    collection = request.registry[COLLECTIONS][type_info.name]
    properties = OrderedDict()
    # add a 'readonly' flag to fields that the current user cannot write
    for k, v in schema['properties'].items():
        if 'permission' in v:
            if not request.has_permission(v['permission'], collection):
                v = v.copy()
                v['readonly'] = True
        properties[k] = v
    schema['properties'] = properties
    return schema


@view_config(route_name='schema', request_method='GET',
             decorator=etag_app_version_effective_principals)
def schema(context, request):
    type_name = request.matchdict['type_name']
    types = request.registry[TYPES]
    try:
        type_info = types[type_name]
    except KeyError:
        raise HTTPNotFound(type_name)

    return _annotated_schema(type_info, request)


@view_config(route_name='schemas', request_method='GET',
             decorator=etag_app_version_effective_principals)
def schemas(context, request):
    types = request.registry[TYPES]
    schemas = {}
    for type_info in types.by_item_type.values():
        name = type_info.name
        schemas[name] = _annotated_schema(type_info, request)
    return schemas
