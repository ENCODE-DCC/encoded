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
    if type_ == 'array':
        return schema_mapping(name, schema['items'])

    if type_ == 'object':
        properties = {
            k: schema_mapping(k, v) for k, v in schema['properties'].items()
        }
        return {'properties': properties}

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

    if type_ in ('boolean', 'integer'):
        return {
            'type': type_,
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
                    'encoded_index_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
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


def es_mapping(mapping):
    return {
        '_all': {
            'analyzer': 'encoded_index_analyzer'
        },
        'properties': {
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
                'include_in_all': False,
                'properties': {}
            },
            'principals_allowed_view': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'embedded_uuid_closure': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'link_uuid_closure': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'keys': {
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
            'url': {
                'type': 'string',
                'include_in_all': False,
                'index': 'not_analyzed'
            },
            'audit': {
                'type': 'object',
                'include_in_all': False,
                'properties': {
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
                    },
                },
            }
        }
    }


def collection_mapping(collection, embed=True):
    schema = collection.schema
    if schema is None:
        return None

    mapping = schema_mapping(collection.item_type, schema)

    merged_rev = collection.Item.merged_rev
    merged_template_type = collection.Item.merged_template_type

    calculated_props = list(schema.get('calculated_props', ()))
    calculated_props.extend(['@id', '@type'])
    calculated_props.extend(merged_rev.keys())

    for name in calculated_props:
        mapping['properties'][name] = schema_mapping(name, {'type': 'string'})

    if not embed:
        return mapping

    root = find_root(collection)

    for prop in collection.Item.embedded:
        new_mapping = mapping
        new_schema = schema

        for i, p in enumerate(prop.split('.')):
            if i == 0 and p in merged_rev:
                name = merged_rev[p][0]
            elif i == 0 and p in merged_template_type:
                name = merged_template_type[p]
            else:
                if p not in new_schema['properties']:
                    if p in root[name].Item.merged_rev:
                        name = root[name].Item.merged_rev[p][0]
                    else:
                        name = root[name].Item.merged_template_type[p]
                else:
                    try:
                        name = new_schema['properties'][p]['linkTo']
                    except KeyError:
                        name = new_schema['properties'][p]['items']['linkTo']

            # XXX Need to union with mouse_donor here
            if name == 'donor':
                name = 'human_donor'

            # XXX file has "linkTo": ["experiment", "dataset"]

            # Check if mapping for property is already an object
            # multiple subobjects may be embedded, so be carful here
            try:
                new_mapping['properties'][p]['properties']
            except KeyError:
                new_mapping['properties'][p] = collection_mapping(
                    root.by_item_type[name], embed=False)

            new_mapping = new_mapping['properties'][p]
            new_schema = root[name].schema

    boost_values = schema.get('boost_values', ())
    for value in boost_values:
        props = value.split('.')
        new_mapping = mapping['properties']
        for prop in props:
            if len(props) == props.index(prop) + 1:
                new_mapping[prop]['boost'] = boost_values[value]
                new_mapping[prop]['copy_to'] = ['encoded_all_ngram', 'encoded_all_standard', 'encoded_all_untouched']
                new_mapping = mapping['properties']
            else:
                new_mapping = new_mapping[prop]['properties']
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
        collections = ['meta'] + root.by_item_type.keys()

    for collection_name in collections:
        if collection_name == 'meta':
            doc_type = 'meta'
            mapping = META_MAPPING
        else:
            doc_type = collection_name
            collection = root.by_item_type[collection_name]
            mapping = collection_mapping(collection)

        if mapping is None:
            continue  # Testing collections
        if dry_run:
            print json.dumps(
                sorted_dict({index: {doc_type: mapping}}), indent=4)
            continue

        if collection_name is not 'meta':
            mapping = es_mapping(mapping)

        try:
            es.indices.put_mapping(index=index, doc_type=doc_type, body={doc_type: mapping})
        except:
            log.info("Could not create mapping for the collection %s", doc_type)
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
