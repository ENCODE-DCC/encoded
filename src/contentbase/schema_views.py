from collections import OrderedDict
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from .interfaces import COLLECTIONS


def includeme(config):
    config.add_route('schemas', '/profiles/')
    config.add_route('schema', '/profiles/{type_name}.json')
    config.scan(__name__)


def _annotated_schema(collection, request):
    schema = collection.type_info.schema.copy()
    schema['@type'] = ['JSONSchema']

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


@view_config(route_name='schema', request_method='GET')
def schema(context, request):
    type_name = request.matchdict['type_name']
    collections = request.registry[COLLECTIONS]
    try:
        collection = collections[type_name]
    except KeyError:
        raise HTTPNotFound(type_name)

    return _annotated_schema(collection, request)


@view_config(route_name='schemas', request_method='GET')
def schemas(context, request):
    collections = request.registry[COLLECTIONS]
    schemas = {}
    for collection in collections.by_item_type.values():
        name = collection.type_info.name
        schemas[name] = _annotated_schema(collection, request)
    return schemas
