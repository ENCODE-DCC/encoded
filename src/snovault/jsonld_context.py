from snovault import (
    TYPES,
)
from pyramid.events import (
    ApplicationCreated,
    subscriber,
)
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from urllib.parse import (
    quote,
    urlparse,
)
from .util import ensurelist


def includeme(config):
    settings = config.registry.settings
    jsonld_base = settings.setdefault('snovault.jsonld.terms_namespace', '/terms/')
    settings.setdefault('snovault.jsonld.terms_prefix', 'term')
    term_path = urlparse(jsonld_base).path

    config.add_route('jsonld_context', term_path)
    config.add_route('jsonld_context_no_slash', term_path.rstrip('/'))
    config.add_route('jsonld_term', term_path + '{term}')
    config.scan(__name__)


@subscriber(ApplicationCreated)
def make_jsonld_context(event):
    app = event.app
    registry = app.registry
    types = registry[TYPES]
    jsonld_base = registry.settings['snovault.jsonld.terms_namespace']
    prefix = registry.settings['snovault.jsonld.terms_prefix']
    term_path = urlparse(jsonld_base).path

    context = {
        prefix: jsonld_base,
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
        'portal': prefix + ':Portal',
        'search': prefix + ':Search',
        'collection': prefix + ':Collection',
    }

    for item_type, type_info in types.by_item_type.items():
        if item_type.startswith('testing_'):
            continue
        schema = type_info.schema
        context.update(context_from_schema(
            schema, prefix, type_info.name, type_info.base_types))

    namespaces = registry.settings.get('snovault.jsonld.namespaces', {})
    context.update(namespaces)

    ontology = {
        '@context': context,
        '@type': 'owl:Ontology',
        '@id': term_path,
    }

    defines = ontology['defines'] = {}
    for type_name in ['Item', 'Collection', 'Portal', 'Search']:
        defines[type_name] = {
            '@id': term_path + type_name,
            '@type': 'rdfs:Class',
        }

    # These are broken definitions
    BROKEN = {
        '@id': prefix + ':BrokenPropertyOrClass',
        'owl:unionOf': [
            'rdf:Property',
            'rdfs:Class',
        ],
        '@type': 'owl:Class',
    }

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

    for item_type, type_info in types.by_item_type.items():
        if item_type.startswith('testing_'):
            continue
        schema = type_info.schema
        iter_defs = ontology_from_schema(
            schema, prefix, term_path, item_type, type_info.name, type_info.base_types)

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
                defines['BrokenPropertyOrClass'] = BROKEN

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

    app.registry['snovault.jsonld.context'] = ontology


def context_from_schema(schema, prefix, class_name, base_types):
    jsonld_context = {}

    for type_name in base_types + [class_name, class_name + 'Collection']:
        jsonld_context[type_name] = '%s:%s' % (prefix, type_name)

    for name, subschema in schema.get('properties', {}).items():
        if name.startswith('@'):
            continue

        if '@id' in subschema and subschema['@id'] is None:
            jsonld_context[name] = None
            continue
        jsonld_context[name] = prop_ld = {
            k: v for k, v in subschema.items() if k.startswith('@')
        }
        if '@reverse' in prop_ld:
            continue
        if '@id' not in prop_ld:
            prop_ld['@id'] = '%s:%s' % (prefix, quote(name, safe=''))

        subschema = subschema.get('items', subschema)
        if '@type' in prop_ld:
            pass
        elif 'linkTo' in subschema or 'linkFrom' in subschema:
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


def ontology_from_schema(schema, prefix, term_path, item_type, class_name, base_types):
    yield {
        '@id': term_path + class_name,
        '@type': 'rdfs:Class',
        'rdfs:subClassOf': [term_path + type_name for type_name in base_types],
        'rdfs:seeAlso': '/profiles/{item_type}.json'.format(item_type=item_type)
    }

    for base_type in base_types[:-1]:
        yield {
            '@id': term_path + base_type,
            '@type': 'rdfs:Class',
            'rdfs:subClassOf': term_path + 'Item',
        }

    yield {
        '@id': term_path + class_name + 'Collection',
        '@type': 'rdfs:Class',
        'rdfs:subClassOf': [term_path + 'Collection'],
    }

    for name, subschema in schema.get('properties', {}).items():
        if name.startswith('@'):
            continue

        if '@id' in subschema and subschema['@id'] is None:
            continue
        if '@reverse' in subschema:
            continue

        prop_ld = {
            '@id': subschema.get('@id', term_path + quote(name, safe='')),
            '@type': 'rdf:Property',
            'rdfs:domain': term_path + class_name,
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
    return request.registry['snovault.jsonld.context']


@view_config(route_name='jsonld_term', request_method='GET')
def jsonld_term(context, request):
    ontology = request.registry['snovault.jsonld.context']
    term = request.matchdict['term']
    try:
        return ontology['defines'][term]
    except KeyError:
        raise HTTPNotFound(term)
