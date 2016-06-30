"""\
Example.

To load the initial data:

    %(prog)s production.ini

"""
from pyramid.paster import get_app
from elasticsearch import RequestError
from functools import reduce
from snovault import (
    COLLECTIONS,
    TYPES,
)
from snovault.schema_utils import combine_schemas
from .interfaces import ELASTIC_SEARCH
import collections
import json
import logging



log = logging.getLogger(__name__)


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

PATH_FIELDS = ['submitted_file_name']
NON_SUBSTRING_FIELDS = ['uuid', '@id', 'submitted_by', 'md5sum', 'references', 'submitted_file_name']


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
            'include_in_all': False,
            'properties': properties,
        }

    if type_ == ["number", "string"]:
        return {
            'type': 'string',
            'copy_to': [],
            'index': 'not_analyzed',
            'fields': {
                'value': {
                    'type': 'float',
                    'copy_to': '',
                    'ignore_malformed': True,
                    'copy_to': []
                },
                'raw': {
                    'type': 'string',
                    'index': 'not_analyzed'
                }
            }
        }

    if type_ == 'boolean':
        return {
            'type': 'string',
            'store': True,
            'fields': {
                'raw': {
                    'type': 'string',
                    'index': 'not_analyzed'
                }
            }
        }

    if type_ == 'string':

        sub_mapping = {
            'type': 'string',
            'store': True
        }

        if schema.get('elasticsearch_mapping_index_type'):
             if schema.get('elasticsearch_mapping_index_type')['default'] == 'analyzed':
                return sub_mapping
        else:
            sub_mapping.update({
                            'fields': {
                                'raw': {
                                    'type': 'string',
                                    'index': 'not_analyzed'
                                }
                            }
                        })
            # these fields are unintentially partially matching some small search
            # keywords because fields are analyzed by nGram analyzer
        if name in NON_SUBSTRING_FIELDS:
            if name in PATH_FIELDS:
                sub_mapping['index_analyzer'] = 'snovault_path_analyzer'
            else:
                sub_mapping['index'] = 'not_analyzed'
            sub_mapping['include_in_all'] = False
        return sub_mapping

    if type_ == 'number':
        return {
            'type': 'float',
            'store': True,
            'fields': {
                'raw': {
                    'type': 'string',
                    'index': 'not_analyzed'
                }
            }
        }

    if type_ == 'integer':
        return {
            'type': 'long',
            'store': True,
            'fields': {
                'raw': {
                    'type': 'string',
                    'index': 'not_analyzed'
                }
            }
        }


def index_settings():
    return {
        'index': {
            'number_of_shards': 1,
            'merge': {
                'policy': {
                    'max_merged_segment': '2gb',
                    'max_merge_at_once': 5
                }
            },
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
                        'tokenizer': 'whitespace',
                        'char_filter': 'html_strip',
                        'filter': [
                            'standard',
                            'lowercase',
                        ]
                    },
                    'snovault_index_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'whitespace',
                        'char_filter': 'html_strip',
                        'filter': [
                            'standard',
                            'lowercase',
                            'asciifolding',
                            'substring'
                        ]
                    },
                    'snovault_search_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'whitespace',
                        'filter': [
                            'standard',
                            'lowercase',
                            'asciifolding'
                        ]
                    },
                    'snovault_path_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'snovault_path_tokenizer',
                        'filter': ['lowercase']
                    }
                },
                'tokenizer': {
                    'snovault_path_tokenizer': {
                        'type': 'path_hierarchy',
                        'reverse': True
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
            'index': 'analyzed', 
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
            'enabled': True,
            'index_analyzer': 'snovault_index_analyzer',
            'search_analyzer': 'snovault_search_analyzer'
        },
        'dynamic_templates': [
            {
                'template_principals_allowed': {
                    'path_match': "principals_allowed.*",
                    'mapping': {
                        'type': 'string',
                        'index': 'not_analyzed',
                    },
                },
            },
            {
                'template_unique_keys': {
                    'path_match': "unique_keys.*",
                    'mapping': {
                        'type': 'string',
                        'index': 'not_analyzed',
                    },
                },
            },
            {
                'template_links': {
                    'path_match': "links.*",
                    'mapping': {
                        'type': 'string',
                        'index': 'not_analyzed',
                    },
                },
            },
        ],
        'properties': {
            'uuid': {
                'type': 'string',
                'index': 'not_analyzed',
                'include_in_all': False,
            },
            'tid': {
                'type': 'string',
                'index': 'not_analyzed',
                'include_in_all': False,
            },
            'item_type': {
                'type': 'string',
                'index': 'not_analyzed'
            },
            'embedded': mapping,
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
                    'INTERNAL_ACTION': {
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

            s = reduce(combine_schemas, (types[t].schema for t in ref_types))

            # Check if mapping for property is already an object
            # multiple subobjects may be embedded, so be carful here
            if m['properties'][p]['type'] == 'string':
                m['properties'][p] = schema_mapping(p, s)

            m = m['properties'][p]

    boost_values = schema.get('boost_values', None)
    if boost_values is None:
        boost_values = {
            prop_name: 1.0
            for prop_name in ['@id', 'title']
            if prop_name in mapping['properties']
        }
    for name, boost in boost_values.items():
        props = name.split('.')
        last = props.pop()
        new_mapping = mapping['properties']
        for prop in props:
            new_mapping = new_mapping[prop]['properties']
        new_mapping[last]['boost'] = boost
        if last in NON_SUBSTRING_FIELDS:
            new_mapping[last]['include_in_all'] = False
            if last in PATH_FIELDS:
                new_mapping[last]['index_analyzer'] = 'snovault_path_analyzer'
            else:
                new_mapping[last]['index'] = 'not_analyzed'
        else:
            new_mapping[last]['index_analyzer'] = 'snovault_index_analyzer'
            new_mapping[last]['search_analyzer'] = 'snovault_search_analyzer'
            new_mapping[last]['include_in_all'] = True

    # Automatic boost for uuid
    if 'uuid' in mapping['properties']:
        mapping['properties']['uuid']['index'] = 'not_analyzed' 
        mapping['properties']['uuid']['include_in_all'] = False
    return mapping


def run(app, collections=None, dry_run=False):
    index = app.registry.settings['snovault.elasticsearch.index']
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
        collections = ['meta'] + list(registry[COLLECTIONS].by_item_type.keys())

    for collection_name in collections:
        if collection_name == 'meta':
            doc_type = 'meta'
            mapping = META_MAPPING
        else:
            doc_type = collection_name
            collection = registry[COLLECTIONS].by_item_type[collection_name]
            mapping = type_mapping(registry[TYPES], collection.type_info.item_type)

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
    logging.getLogger('snovault').setLevel(logging.DEBUG)

    return run(app, args.item_type, args.dry_run)


if __name__ == '__main__':
    main()
