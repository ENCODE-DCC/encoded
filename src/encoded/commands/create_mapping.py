"""\
Example.

To load the initial data:

    %(prog)s production.ini

"""
from pyramid.paster import get_app
from elasticsearch import RequestError
from ..contentbase import TYPES
from ..indexing import ELASTIC_SEARCH
import collections
import json
import logging

EPILOG = __doc__

log = logging.getLogger(__name__)

# An index to store non-content metadata
META_MAPPING = {
    'dynamic_templates': [
        {
            'store_generic': {
                'match': '*',
                'mapping': {
                    'index': 'no',
                    'store': 'yes',
                },
            },
        },
    ],
}


def sorted_pairs_hook(pairs):
    return collections.OrderedDict(sorted(pairs))


def sorted_dict(d):
    return json.loads(json.dumps(d), object_pairs_hook=sorted_pairs_hook)


def schema_mapping(name, schema):
    if 'linkFrom' in schema:
        type_ = 'string'
    else:
        type_ = schema['type']

    # Elasticsearch handles multiple values for a field
    if type_ == 'array' and schema['items']:
        return schema_mapping(name, schema['items'])

    if type_ == 'object':
        properties = {}
        for k, v in schema.get('properties', {}).items():
            mapping = schema_mapping(k, v)
            if mapping is not None:
                properties[k] = mapping
        return {
            'type': 'object',
            'properties': properties,
        }

    if type_ == ["number", "string"]:
        return {
            'type': 'string',
            'include_in_all': False,
            'copy_to': [],
            'index': 'not_analyzed',
            'fields': {
                'value': {
                    'type': 'float',
                    'copy_to': '',
                    'ignore_malformed': True,
                    'include_in_all': False,
                    'copy_to': []
                }
            }
        }

    if type_ == 'string':
        return {
            'type': 'string',
            'include_in_all': False,
            'copy_to': [],
            'index': 'not_analyzed',
        }

    if type_ == 'number':
        return {
            'type': 'float',
            'copy_to': [],
            'include_in_all': False
        }

    if type_ == 'integer':
        return {
            'type': 'long',
            'copy_to': [],
            'include_in_all': False
        }

    if type_ == 'boolean':
        return {
            'type': 'boolean',
            'copy_to': [],
            'include_in_all': False
        }


def index_settings():
    return {
        'index': {
            'analysis': {
                'filter': {
                    'substring': {
                        'type': 'nGram',
                        'min_gram': 1,
                        'max_gram': 33
                    }
                },
                'analyzer': {
                    'default': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'char_filter': 'html_strip',
                        'filter': [
                            'standard',
                            'lowercase',
                        ]
                    },
                    'encoded_index_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'char_filter': 'html_strip',
                        'filter': [
                            'standard',
                            'lowercase',
                            'asciifolding',
                            'substring'
                        ]
                    },
                    'encoded_search_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': [
                            'standard',
                            'lowercase',
                            'asciifolding'
                        ]
                    }
                }
            }
        }
    }


def audit_mapping():
    return {
        'category': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'detail': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'level_name': {
            'type': 'string',
            'index': 'not_analyzed',
        },
        'level': {
            'type': 'integer',
        }
    }


def es_mapping(mapping):
    return {
        '_all': {
            'analyzer': 'encoded_index_analyzer'
        },
        'dynamic_templates': [
            {
                'template_principals_allowed': {
                    'path_match': "principals_allowed.*",
                    'mapping': {
                        'type': 'string',
                        'include_in_all': False,
                        'index': 'not_analyzed',
                    },
                },
            },
            {
                'template_unique_keys': {
                    'path_match': "unique_keys.*",
                    'mapping': {
                        'type': 'string',
                        'include_in_all': False,
                        'index': 'not_analyzed',
                    },
                },
            },
            {
                'template_links': {
                    'path_match': "links.*",
                    'mapping': {
                        'type': 'string',
                        'include_in_all': False,
                        'index': 'not_analyzed',
                    },
                },
            },
        ],
        'properties': {
            'uuid': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'tid': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'item_type': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'embedded': mapping,
            'encoded_all_ngram': {
                'type': 'string',
                'include_in_all': False,
                'boost': 1,
                'search_analyzer': 'encoded_search_analyzer',
                'index_analyzer': 'encoded_index_analyzer'
            },
            'encoded_all_standard': {
                'type': 'string',
                'include_in_all': False,
                'boost': 2
            },
            'encoded_all_untouched': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed',
                'boost': 3
            },
            'object': {
                'type': 'object',
                'enabled': False,
                'include_in_all': False,
            },
            'properties': {
                'type': 'object',
                'enabled': False,
                'include_in_all': False,
            },
            'propsheets': {
                'type': 'object',
                'enabled': False,
                'include_in_all': False,
            },
            'principals_allowed': {
                'type': 'object',
                'include_in_all': False,
            },
            'embedded_uuids': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'linked_uuids': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'unique_keys': {
                'type': 'object',
                'include_in_all': False,
            },
            'links': {
                'type': 'object',
                'include_in_all': False,
            },
            'paths': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'audit': {
                'type': 'object',
                'include_in_all': False,
                'properties': {
                    'ERROR': {
                        'type': 'object',
                        'properties': audit_mapping()
                    },
                    'NOT_COMPLIANT': {
                        'type': 'object',
                        'properties': audit_mapping()
                    },
                    'WARNING': {
                        'type': 'object',
                        'properties': audit_mapping()
                    },
                    'DCC_ACTION': {
                        'type': 'object',
                        'properties': audit_mapping()
                    },
                },
            }
        }
    }


def combined_mapping(types, *item_types):
    combined = {
        'type': 'object',
        'properties': {},
    }
    for item_type in item_types:
        schema = types[item_type].schema
        mapping = schema_mapping(item_type, schema)
        for k, v in mapping['properties'].items():
            if k in combined:
                assert v == combined[k]
            else:
                combined[k] = v

    return combined


def aslist(value):
    if isinstance(value, basestring):
        return [value]
    return value


def combine_schemas(a, b):
    if a == b:
        return a
    if not a:
        return b
    if not b:
        return a
    combined = {}
    for name in set(a.keys()).intersection(b.keys()):
        if a[name] == b[name]:
            combined[name] = a[name]
        elif name == 'type':
            combined[name] = sorted(set(aslist(a[name]) + aslist(b[name])))
        elif name == 'properties':
            combined[name] = {}
            for k in set(a[name].keys()).intersection(b[name].keys()):
                combined[name][k] = combine_schemas(a[name][k], b[name][k])
            for k in set(a[name].keys()).difference(b[name].keys()):
                combined[name][k] = a[name][k]
            for k in set(b[name].keys()).difference(a[name].keys()):
                combined[name][k] = b[name][k]
        elif name == 'items':
            combined[name] = combine_schemas(a[name], b[name])
    for name in set(a.keys()).difference(b.keys()):
        combined[name] = a[name]
    for name in set(b.keys()).difference(a.keys()):
        combined[name] = b[name]
    return combined


def type_mapping(types, item_type, embed=True):
    type_info = types[item_type]
    schema = type_info.schema
    mapping = schema_mapping(item_type, schema)
    if not embed:
        return mapping

    for prop in type_info.embedded:
        s = schema
        m = mapping

        for p in prop.split('.'):
            ref_types = None

            subschema = s.get('properties', {}).get(p)
            if subschema is None:
                msg = 'Unable to find schema for %r embedding %r in %r' % (p, prop, item_type)
                raise ValueError(msg)

            subschema = subschema.get('items', subschema)
            if 'linkFrom' in subschema:
                _ref_type, _ = subschema['linkFrom'].split('.', 1)
                ref_types = [_ref_type]
            elif 'linkTo' in subschema:
                ref_types = subschema['linkTo']
                if not isinstance(ref_types, list):
                    ref_types = [ref_types]

            if ref_types is None:
                m = m['properties'][p]
                s = subschema
                continue

            ref_types = set(ref_types)
            abstract = [t for t in ref_types if t in types.abstract]
            for t in abstract:
                ref_types.update(types.abstract[t].subtypes)
            concrete = [t for t in ref_types if t in types.types]

            s = {}
            for t in concrete:
                s = combine_schemas(s, types[t].schema)

            # Check if mapping for property is already an object
            # multiple subobjects may be embedded, so be carful here
            if m['properties'][p]['type'] == 'string':
                m['properties'][p] = schema_mapping(p, s)

            m = m['properties'][p]

    boost_values = schema.get('boost_values', ())
    for value in boost_values:
        props = value.split('.')
        last = props.pop()
        new_mapping = mapping['properties']
        for prop in props:
            new_mapping = new_mapping[prop]['properties']

        new_mapping[last]['boost'] = boost_values[value]
        new_mapping[last]['copy_to'] = \
            ['encoded_all_ngram', 'encoded_all_standard', 'encoded_all_untouched']

    # Automatic boost for uuid
    if 'uuid' in mapping['properties']:
        mapping['properties']['uuid']['boost'] = 1.0
        mapping['properties']['uuid']['copy_to'] = ['encoded_all_untouched']
    return mapping


def run(app, collections=None, dry_run=False):
    index = 'encoded'
    registry = app.registry
    if not dry_run:
        es = app.registry[ELASTIC_SEARCH]
        try:
            es.indices.create(index=index, body=index_settings())
        except RequestError:
            if collections is None:
                es.indices.delete(index=index)
                es.indices.create(index=index, body=index_settings())

    if not collections:
        collections = ['meta'] + list(registry['collections'].by_item_type.keys())

    for collection_name in collections:
        if collection_name == 'meta':
            doc_type = 'meta'
            mapping = META_MAPPING
        else:
            doc_type = collection_name
            collection = registry['collections'].by_item_type[collection_name]
            mapping = type_mapping(registry[TYPES], collection.item_type)

        if mapping is None:
            continue  # Testing collections
        if dry_run:
            print(json.dumps(sorted_dict({index: {doc_type: mapping}}), indent=4))
            continue

        if collection_name is not 'meta':
            mapping = es_mapping(mapping)

        try:
            es.indices.put_mapping(index=index, doc_type=doc_type, body={doc_type: mapping})
        except:
            log.exception("Could not create mapping for the collection %s", doc_type)
        else:
            es.indices.refresh(index=index)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Create Elasticsearch mapping", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--item-type', action='append', help="Item type")
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument(
        '--dry-run', action='store_true', help="Don't post to ES, just print")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    app = get_app(args.config_uri, args.app_name)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    return run(app, args.item_type, args.dry_run)


if __name__ == '__main__':
    main()
