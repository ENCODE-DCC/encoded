from collections import OrderedDict
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config


def includeme(config):
    config.add_route('schemas', '/profiles/')
    config.add_route('schema', '/profiles/{item_type}.json')
    config.scan(__name__)


def _filtered_schema(collection, request):
    schema = collection.type_info.schema.copy()

    properties = OrderedDict()
    for k, v in schema['properties'].items():
        if 'permission' in v:
            if not request.has_permission(v['permission'], collection):
                continue
        properties[k] = v
    schema['properties'] = properties
    return schema


@view_config(route_name='schema', request_method='GET')
def schema(context, request):
    item_type = request.matchdict['item_type']
    try:
        collection = context.by_item_type[item_type]
    except KeyError:
        raise HTTPNotFound(item_type)

    return _filtered_schema(collection, request)


@view_config(route_name='schemas', request_method='GET')
def schemas(context, request):
    schemas = {}
    for typename, collection in context.by_item_type.items():
        schemas[typename] = _filtered_schema(collection, request)
    return schemas
