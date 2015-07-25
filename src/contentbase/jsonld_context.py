from pyramid.events import (
    ApplicationCreated,
    subscriber,
)
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from urllib.parse import urlparse
from .util import ensurelist


def includeme(config):
    settings = config.registry.settings
    jsonld_base = settings.setdefault('contentbase.jsonld.terms_namespace', '/terms/')
    settings.setdefault('contentbase.jsonld.terms_prefix', 'term')
    term_path = urlparse(jsonld_base).path

    config.add_route('jsonld_context', term_path)
    config.add_route('jsonld_context_no_slash', term_path.rstrip('/'))
    config.add_route('jsonld_term', term_path + '{term}')
    config.scan(__name__)


@subscriber(ApplicationCreated)
def make_jsonld_context(event):
    app = event.app
    registry = app.registry
    root = app.root_factory(app)
    jsonld_base = registry.settings['contentbase.jsonld.terms_namespace']
    prefix = registry.settings['contentbase.jsonld.terms_prefix']
    term_path = urlparse(jsonld_base).path

    context = {
        prefix: jsonld_base,
        '@base': jsonld_base,
        'dc': 'http://purl.org/dc/terms/',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'owl': 'http://www.w3.org/2002/07/owl#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'defines': {
            '@container': '@index',
            '@reverse': 'rdfs:isDefinedBy'
        },
        'owl:unionOf': {
            '@container': '@list',
            '@type': '@id'
        },
        'rdfs:isDefinedBy': {
            '@type': '@id',
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
        'rdfs:seeAlso': {
            '@type': '@id',
        },
        'portal': prefix + ':portal',
        'search': prefix + ':search',
        'collection': prefix + ':collection',
    }

    for name, collection in root.by_item_type.items():
        if name.startswith('testing_'):
            continue
        schema = collection.type_info.schema
        context.update(context_from_schema(
            schema, prefix, collection.item_type, collection.type_info.base_types))

    namespaces = registry.settings.get('contentbase.jsonld.namespaces', {})
    context.update(namespaces)

    ontology = {
        '@context': context,
        '@type': 'owl:Ontology',
        '@id': term_path,
    }

    defines = ontology['defines'] = {}
    for type_name in ['item', 'collection', 'portal', 'search']:
        defines[type_name] = {
            '@id': term_path + type_name,
            '@type': 'rdfs:Class',
        }

    # These are broken definitions
    defines['BrokenPropertyOrClass'] = {
        '@id': prefix + ':BrokenPropertyOrClass',
        'owl:unionOf': [
            'rdf:Property',
            'rdfs:Class',
        ],
        '@type': 'owl:Class',
    },

    MERGED_PROPS = [
        'rdfs:subClassOf',
        'rdfs:subPropertyOf',
        'rdfs:label',
        'rdfs:comment',
        'rdfs:isDefinedBy',
        'rdfs:seeAlso',
    ]
    MERGED_TYPES = [
        'rdfs:range',
        'rdfs:domain',
    ]

    for name, collection in root.by_item_type.items():
        if name.startswith('testing_'):
            continue
        schema = collection.type_info.schema
        iter_defs = ontology_from_schema(
            schema, prefix, term_path, collection.item_type, collection.type_info.base_types)

        for definition in iter_defs:
            if definition['@id'].startswith(term_path):
                name = definition['@id'][len(term_path):]
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
                    set(ensurelist(existing.get(prop, [])) + ensurelist(definition[prop])))

            if existing['@type'] != definition['@type']:
                existing['@type'] = prefix + ':BrokenPropertyOrClass'

            for prop in MERGED_TYPES:
                if prop not in definition:
                    continue
                if prop not in existing:
                    existing[prop] = definition[prop]
                    continue
                if existing[prop] == definition[prop]:
                    continue
                classes = set()
                for d in [definition, existing]:
                    if isinstance(d[prop], dict):
                        classes.update(d[prop]['owl:unionOf'])
                    else:
                        classes.add(d[prop])
                if len(classes) == 1:
                    existing[prop] = classes.pop()
                else:
                    existing[prop] = {
                        '@type': 'owl:Class',
                        'owl:unionOf': sorted(classes),
                    }

    app.registry['contentbase.jsonld.context'] = ontology


def context_from_schema(schema, prefix, item_type, base_types):
    jsonld_context = {}

    for type_name in base_types + [item_type, item_type + '_collection']:
        jsonld_context[type_name] = '%s:%s' % (prefix, type_name)

    for name, subschema in schema.get('properties', {}).items():
        if '@id' in subschema and subschema['@id'] is None:
            jsonld_context[name] = None
            continue
        jsonld_context[name] = prop_ld = {
            k: v for k, v in subschema.items() if k.startswith('@')
        }
        if '@reverse' in prop_ld:
            continue
        if '@id' not in prop_ld:
            prop_ld['@id'] = '%s:%s' % (prefix, type_name)

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


def ontology_from_schema(schema, prefix, term_path, item_type, base_types):
    yield {
        '@id': term_path + item_type,
        '@type': 'rdfs:Class',
        'rdfs:subClassOf': [term_path + type_name for type_name in base_types],
        'rdfs:seeAlso': '/profiles/{item_type}.json'.format(item_type=item_type)
    }

    for base_type in base_types[:-1]:
        yield {
            '@id': term_path + base_type,
            '@type': 'rdfs:Class',
            'rdfs:subClassOf': term_path + 'item',
        }

    yield {
        '@id': term_path + item_type + '_collection',
        '@type': 'rdfs:Class',
        'rdfs:subClassOf': [term_path + 'collection'],
    }

    for name, subschema in schema.get('properties', {}).items():
        if '@id' in subschema and subschema['@id'] is None:
            continue
        if '@reverse' in subschema:
            continue

        prop_ld = {
            '@id': subschema.get('@id', term_path + name),
            '@type': 'rdf:Property',
            'rdfs:domain': term_path + item_type,
        }

        if 'rdfs:subPropertyOf' in subschema:
            prop_ld['rdfs:subPropertyOf'] = ensurelist(subschema['rdfs:subPropertyOf'])

        subschema = subschema.get('items', subschema)
        if 'title' in subschema:
            prop_ld['rdfs:label'] = subschema['title']

        if 'description' in subschema:
            prop_ld['rdfs:comment'] = subschema['description']

        links = ensurelist(subschema.get('linkTo', []))
        if subschema.get('linkFrom'):
            links.append(subschema['linkFrom'].split('.')[0])
        if len(links) == 1:
            links, = links
            prop_ld['rdfs:range'] = term_path + links
        elif len(links) > 1:
            prop_ld['rdfs:range'] = {
                '@type': 'owl:Class',
                'owl:unionOf': [term_path + type_name for type_name in ensurelist(links)],
            }

        yield prop_ld


@view_config(route_name='jsonld_context_no_slash', request_method='GET')
@view_config(route_name='jsonld_context', request_method='GET')
def jsonld_context(context, request):
    return request.registry['contentbase.jsonld.context']


@view_config(route_name='jsonld_term', request_method='GET')
def jsonld_term(context, request):
    ontology = request.registry['contentbase.jsonld.context']
    term = request.matchdict['term']
    try:
        return ontology['defines'][term]
    except KeyError:
        raise HTTPNotFound(term)


# @subscriber(BeforeRender)  # disable for now
def add_jsonld_context(event):
    request = event['request']
    value = event.rendering_val
    if ('@id' in value or '@graph' in value) and '@context' not in value:
        value['@context'] = request.route_path('jsonld_context')
