from itertools import chain
from pkg_resources import resource_stream
from pyramid.events import (
    ApplicationCreated,
    BeforeRender,
    subscriber,
)
from pyramid.view import view_config
import json


jsonld_base = 'https://www.encodeproject.org/terms/'


@subscriber(ApplicationCreated)
def make_jsonld_context(event):
    app = event.app
    root = app.root_factory(app)
    merged = {
        'portal': jsonld_base + 'portal',
        'search': jsonld_base + 'search',
    }

    for name, collection in root.by_item_type.iteritems():
        if name.startswith('testing-') or collection.schema is None:
            continue
        merged.update(context_from_schema(
            collection.schema, jsonld_base, collection.item_type, collection.Item.base_types))

    namespaces = json.load(resource_stream(__name__, '../schemas/namespaces.json'))
    merged.update(namespaces)
    app.registry['encoded.jsonld_context'] = merged


def context_from_schema(schema, jsonld_base, item_type, base_types):
    jsonld_context = {}

    for type_name in base_types + [item_type]:
        jsonld_context[type_name] = jsonld_base + type_name

    all_props = chain(
        schema.get('properties', {}).iteritems(),
        schema.get('calculated_props', {}).iteritems(),
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


@subscriber(ApplicationCreated)
def make_jsonld_terms(event):
    app = event.app
    root = app.root_factory(app)

    ontology = {
        '@context': {
            '@base': jsonld_base,
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'defines': {
                '@id': 'owl:defines',
                '@container': '@index',
            },
            'rdfs:Property': {
                '@type': '@id',
            },
            'rdfs:subPropertyOf': {
                '@type': '@id',
            },
            'rdfs:Class': {
                '@type': '@id',
            },
            'rdfs:subClassOf': {
                '@type': '@id',
            },
            'rdfs:domain': {
                '@type': '@id',
            },
            'rdfs:range': {
                '@type': '@id',
            },
            'rdf:type': {
                '@type': '@id',
            },
        },
        '@type': 'owl:Ontology',
        '@id': '',
        'defines': {
            'item': {
                '@id': 'item',
                'rdf:type': 'rdfs:Class',
            },
            'collection': {
                '@id': 'collection',
                'rdf:type': 'rdfs:Class',
            },
        },
    }

    defines = ontology['defines']
    for name, collection in root.by_item_type.iteritems():
        if name.startswith('testing-') or collection.schema is None:
            continue
        iter_defs = ontology_from_schema(
            collection.schema, collection.item_type, collection.Item.base_types)

        for definition in iter_defs:
            defines[definition['@id']] = definition

    app.registry['encoded.jsonld_terms'] = ontology


def ontology_from_schema(schema, item_type, base_types):
    yield {
        '@id': item_type,
        'rdf:type': 'rdfs:Class',
        'rdfs:subClassOf': base_types,
    }
    for base_type in base_types[:-1]:
        yield {
            '@id': base_type,
            'rdf:type': 'rdfs:Class',
            'rdfs:subClassOf': 'item',
        }

    all_props = chain(
        schema.get('properties', {}).iteritems(),
        schema.get('calculated_props', {}).iteritems(),
    )
    for name, schema in all_props:
        if '@id' in schema and schema['@id'] is None:
            continue
        if '@reverse' in schema:
            continue
        prop_ld = {
            '@id': schema.get('@id', name),
            '@type': schema.get('rdf:type', 'rdf:Property'),
            'rdfs:domain': schema.get('rdf:domain', []),
        }
        prop_ld['rdfs:domain'].append(item_type)
        if 'rdfs:subPropertyOf' in schema:
            prop_ld['rdfs:subPropertyOf'] = schema['rdfs:subPropertyOf']

        if 'title' in schema:
            prop_ld['rdfs:label'] = schema['title']

        if 'description' in schema:
            prop_ld['rdfs:comment'] = schema['description']

        linkTo = schema.get('items', schema).get('linkTo')
        if isinstance(linkTo, basestring):
            linkTo = [linkTo]
        if linkTo is not None:
            prop_ld['rdfs:range'] = linkTo

        yield prop_ld


@view_config(route_name='jsonld_context', request_method='GET')
def jsonld_context(context, request):
    request.environ['encoded.canonical_redirect'] = False
    return request.registry['encoded.jsonld_context']


@view_config(route_name='jsonld_terms', request_method='GET')
def jsonld_terms(context, request):
    request.environ['encoded.canonical_redirect'] = False
    return request.registry['encoded.jsonld_terms']


# @subscriber(BeforeRender)  # disable for now
def add_jsonld_context(event):
    request = event['request']
    value = event.rendering_val
    if ('@id' in value or '@graph' in value) and '@context' not in value:
        # The context link needs to be a canonicalised URI
        value['@context'] = request.route_url('jsonld_context')
