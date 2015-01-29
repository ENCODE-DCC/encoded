"""\
Example.

To load the initial data:

    %(prog)s production.ini

"""
from pyramid.paster import get_app
from pyramid.traversal import find_root
from elasticsearch import RequestError
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
        'properties': {
            'uuid': {
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
            'principals_allowed': {
                'type': 'object',
                'include_in_all': False,
                '_default_': {
                    'type': 'string',
                    'index': 'not_analyzed',
                },
                'properties': {
                    # 'view' must be specified explicitly to be searched on
                    'view': {
                        'type': 'string',
                        'index': 'not_analyzed',
                    },
                },
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
                '_default_': {
                    'type': 'string',
                    'index': 'not_analyzed',
                },
            },
            'links': {
                'type': 'object',
                'include_in_all': False,
                '_default_': {
                    'type': 'string',
                    'index': 'not_analyzed',
                },
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


def collection_mapping(calculated_properties, collection, embed=True):
    schema = calculated_properties.schema_for(collection.Item)
    mapping = schema_mapping(collection.item_type, schema)
    rev = collection.Item.rev

    for name in rev.keys():
        mapping['properties'][name] = schema_mapping(name, {'type': 'string'})

    if not embed:
        return mapping

    root = find_root(collection)
    for prop in collection.Item.embedded:
        new_mapping = mapping
        new_schema = schema
        new_rev = rev

        for i, p in enumerate(prop.split('.')):
            name = None

            subschema = new_schema.get('properties', {}).get(p)
            if subschema is not None:
                subschema = subschema.get('items', subschema)
                name = subschema.get('linkTo')

            if name is None and p in new_rev:
                name, rev_path = new_rev[p]

            # XXX Need to union with mouse_donor here
            if name == 'donor':
                name = 'human_donor'

            # XXX file has "linkTo": ["experiment", "dataset"]

            # Check if mapping for property is already an object
            # multiple subobjects may be embedded, so be carful here
            if name is not None and new_mapping['properties'][p]['type'] == 'string':
                new_mapping['properties'][p] = collection_mapping(
                    calculated_properties, root.by_item_type[name], embed=False)

            new_mapping = new_mapping['properties'][p]

            if name is not None:
                new_schema = root[name].Item.schema
                new_rev = root[name].Item.rev
            elif subschema is not None:
                new_schema = subschema

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
    root = app.root_factory(app)
    if not dry_run:
        es = app.registry[ELASTIC_SEARCH]
        try:
            es.indices.create(index=index, body=index_settings())
        except RequestError:
            if collections is None:
                es.indices.delete(index=index)
                es.indices.create(index=index, body=index_settings())

    if not collections:
        collections = ['meta'] + list(root.by_item_type.keys())

    calculated_properties = app.registry['calculated_properties']

    for collection_name in collections:
        if collection_name == 'meta':
            doc_type = 'meta'
            mapping = META_MAPPING
        else:
            doc_type = collection_name
            collection = root.by_item_type[collection_name]
            mapping = collection_mapping(calculated_properties, collection)

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
