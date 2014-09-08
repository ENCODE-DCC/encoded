from itertools import chain
from pkg_resources import resource_stream
from pyramid.events import (
    ApplicationCreated,
    subscriber,
)
from pyramid.view import view_config
import json


@subscriber(ApplicationCreated)
def created(event):
    app = event.app
    root = app.root_factory(app)
    jsonld_base = 'https://www.encodeproject.org/ld/'
    merged = {
        'portal': jsonld_base + 'portal',
        'search': jsonld_base + 'search',
    }

    for name, collection in root.by_item_type.iteritems():
        if name.startswith('testing-'):
            continue
        merged.update(context_from_collection(collection, jsonld_base))

    namespaces = json.load(resource_stream(__name__, '../schemas/namespaces.json'))
    merged.update(namespaces)
    app.registry['encoded.jsonld_context'] = merged


def context_from_collection(collection, jsonld_base):
    jsonld_context = {}

    for type_name in collection.Item.base_types + [collection.item_type]:
        jsonld_context[type_name] = jsonld_base + type_name

    if collection.schema is None:
        return jsonld_context

    all_props = chain(
        collection.schema.get('properties', {}).iteritems(),
        collection.schema.get('calculated_props', {}).iteritems(),
    )
    for name, schema in all_props:
        if '@id' in schema and schema['@id'] is None:
            continue
        jsonld_context[name] = prop_ld = {
            k: v for k, v in schema.iteritems() if k.startswith('@')
        }
        if '@reverse' in prop_ld:
            continue
        if '@id' not in prop_ld:
            prop_ld['@id'] = jsonld_base + name
        if '@type' not in prop_ld:
            if 'linkTo' in schema.get('items', schema):
                prop_ld['@type'] = '@id'

    return jsonld_context


@view_config(route_name='jsonld_context', request_method='GET')
def jsonld_context(context, request):
    return request.registry['encoded.jsonld_context']
