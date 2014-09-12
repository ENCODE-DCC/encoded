from itertools import chain
from pkg_resources import resource_stream
from pyramid.events import (
    ApplicationCreated,
    BeforeRender,
    subscriber,
)
from pyramid.view import view_config
import json


jsonld_base = 'https://www.encodeproject.org/terms#'
prefix = 'encode:'


def aslist(value):
    if isinstance(value, basestring):
        return [value]
    return value


def allprops(schema):
    return chain(
        schema.get('properties', {}).iteritems(),
        schema.get('calculated_props', {}).iteritems(),
    )


@subscriber(ApplicationCreated)
def make_jsonld_context(event):
    app = event.app
    root = app.root_factory(app)
    context = {
        'encode': jsonld_base,
        'dc': 'http://purl.org/dc/terms/',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'owl': 'http://www.w3.org/2002/07/owl#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'owl:defines': {
            '@container': '@index',
        },
        'rdfs:subPropertyOf': {
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
        'portal': prefix + 'portal',
        'search': prefix + 'search',
        'collection': prefix + 'collection',
    }

    for name, collection in root.by_item_type.iteritems():
        if name.startswith('testing_') or collection.schema is None:
            continue
        context.update(context_from_schema(
            collection.schema, prefix, collection.item_type, collection.Item.base_types))

    namespaces = json.load(resource_stream(__name__, '../schemas/namespaces.json'))
    context.update(namespaces)

    ontology = {
        '@context': context,
        '@type': 'owl:Ontology',
        '@id': jsonld_base,
    }

    defines = ontology['owl:defines'] = {}
    for type_name in ['item', 'collection', 'portal', 'search']:
        defines[type_name] = {
            '@id': prefix + type_name,
            '@type': 'rdfs:Class',
        }

    MERGED_PROPS = [
        '@type',
        'rdfs:range',
        'rdfs:domain',
        'rdfs:subClassOf',
        'rdfs:subPropertyOf',
        'rdfs:label',
        'rdfs:comment',
    ]

    for name, collection in root.by_item_type.iteritems():
        if name.startswith('testing_') or collection.schema is None:
            continue
        iter_defs = ontology_from_schema(
            collection.schema, prefix, collection.item_type, collection.Item.base_types)

        for definition in iter_defs:
            if definition['@id'].startswith(prefix):
                name = definition['@id'][len(prefix):]
            else:
                name = definition['@id']
            if name not in defines:
                defines[name] = definition
                continue
            existing = defines[name]
            for prop in MERGED_PROPS:
                if prop not in definition:
                    continue
                if prop not in existing:
                    existing[prop] = definition[prop]
                    continue
                if existing[prop] == definition[prop]:
                    continue
                existing[prop] = sorted(
                    set(aslist(existing.get(prop, [])) + aslist(definition[prop])))

    app.registry['encoded.jsonld_context'] = ontology


def context_from_schema(schema, prefix, item_type, base_types):
    jsonld_context = {}

    for type_name in base_types + [item_type, item_type + '_collection']:
        jsonld_context[type_name] = prefix + type_name

    for name, subschema in allprops(schema):
        if '@id' in subschema and subschema['@id'] is None:
            jsonld_context[name] = None
            continue
        jsonld_context[name] = prop_ld = {
            k: v for k, v in subschema.iteritems() if k.startswith('@')
        }
        if '@reverse' in prop_ld:
            continue
        if '@id' not in prop_ld:
            prop_ld['@id'] = prefix + name

        subschema.get('items', subschema)
        if '@type' in prop_ld:
            pass
        elif 'linkTo' in subschema:
            prop_ld['@type'] = '@id'
        elif subschema.get('anyOf') == [{"format": "date-time"}, {"format": "date"}]:
            prop_ld['@type'] = 'xsd:dateTime'
        elif subschema.get('format') == 'date-time':
            prop_ld['@type'] = 'xsd:date'
        elif subschema.get('format') == 'date':
            prop_ld['@type'] = 'xsd:date'
        elif subschema.get('format') == 'uri':
            # Should this be @id?
            prop_ld['@type'] = '@id'
        elif subschema.get('type') == 'integer':
            prop_ld['@type'] = 'xsd:integer'
        elif subschema.get('type') == 'number':
            prop_ld['@type'] = 'xsd:float'
        elif subschema.get('type') == 'boolean':
            prop_ld['@type'] = 'xsd:boolean'

    return jsonld_context


def ontology_from_schema(schema, prefix, item_type, base_types):
    yield {
        '@id': prefix + item_type,
        '@type': 'rdfs:Class',
        'rdfs:subClassOf': [prefix + type_name for type_name in base_types],
    }

    for base_type in base_types[:-1]:
        yield {
            '@id': prefix + base_type,
            '@type': 'rdfs:Class',
            'rdfs:subClassOf': prefix + 'item',
        }

    yield {
        '@id': prefix + item_type + '_collection',
        '@type': 'rdfs:Class',
        'rdfs:subClassOf': [prefix + 'collection'],
    }

    for name, subschema in allprops(schema):
        if '@id' in subschema and subschema['@id'] is None:
            continue
        if '@reverse' in subschema:
            continue

        prop_ld = {
            '@id': subschema.get('@id', prefix + name),
            '@type': 'rdf:Property',
            'rdfs:domain': aslist(subschema.get('rdfs:domain', [])),
        }
        prop_ld['rdfs:domain'].append(prefix + item_type)

        if 'rdfs:subPropertyOf' in subschema:
            prop_ld['rdfs:subPropertyOf'] = aslist(subschema['rdfs:subPropertyOf'])

        subschema.get('items', subschema)
        if 'title' in subschema:
            prop_ld['rdfs:label'] = subschema['title']

        if 'description' in subschema:
            prop_ld['rdfs:comment'] = subschema['description']

        linkTo = subschema.get('linkTo')
        if linkTo is not None:
            prop_ld['rdfs:range'] = [prefix + type_name for type_name in aslist(linkTo)]

        yield prop_ld


@view_config(route_name='jsonld_context', request_method='GET')
def jsonld_context(context, request):
    request.environ['encoded.canonical_redirect'] = False
    return request.registry['encoded.jsonld_context']


# @subscriber(BeforeRender)  # disable for now
def add_jsonld_context(event):
    request = event['request']
    value = event.rendering_val
    if ('@id' in value or '@graph' in value) and '@context' not in value:
        # The context link needs to be a canonicalised URI
        value['@context'] = request.route_url('jsonld_context')
