"""\
Example.

To load the initial data:

    %(prog)s production.ini

"""
from pyramid.paster import get_app
from pyramid.traversal import find_root
from pyelasticsearch import IndexAlreadyExistsError
from ..indexing import ELASTIC_SEARCH
import collections
import json
import logging

EPILOG = __doc__


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

    if type_ == 'string':
        return {
            'type': 'multi_field',
            'fields': {
                # by default ES uses the same named field of a multi_field
                name: {
                    'type': 'string',
                    'search_analyzer': 'encoded_search_analyzer',
                    'index_analyzer': 'encoded_index_analyzer',
                    'include_in_all': False
                },
                'untouched': {
                    'type': 'string',
                    'index': 'not_analyzed',
                    'include_in_all': False,
                    'omit_norms': True,
                },
            },
        }

    if type_ == 'number':
        return {'type': 'float'}

    if type_ in ('boolean', 'integer'):
        return {'type': type_}


def index_settings(index):
    return {
        'settings': {
            'analysis': {
                'filter': {
                    'substring': {
                        'type': 'nGram',
                        'min_gram': 3,
                        'max_gram': 25
                    }
                },
                'analyzer': {
                    'encoded_index_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'keyword',
                        'filter': ['lowercase', 'substring']
                    },
                    'encoded_search_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'keyword',
                        'filter': ['lowercase']
                    }
                }
            }
        }
    }


def collection_mapping(collection, embed=True):
    schema = collection.schema
    if schema is None:
        return None

    mapping = schema_mapping(collection.item_type, schema)

    calculated_props = list(schema.get('calculated_props', ()))
    calculated_props.extend(['@id', '@type'])

    for name in calculated_props:
        mapping['properties'][name] = schema_mapping(name, {'type': 'string'})

    if not embed:
        return mapping

    root = find_root(collection)
    rev_links = collection.Item.rev or {}

    for prop in collection.Item.embedded:
        new_mapping = mapping
        new_schema = schema

        for i, p in enumerate(prop.split('.')):
            if i == 0 and p in rev_links:
                name = rev_links[p][0]
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
                new_mapping[prop]['fields'][prop]['boost'] = boost_values[value]
                if prop == 'assay_term_name':
                    new_mapping[prop]['analyzer'] = 'dash_path'
                del(new_mapping[prop]['fields'][prop]['include_in_all'])
                del(new_mapping[prop]['fields']['untouched']['include_in_all'])
                new_mapping = mapping['properties']
            else:
                new_mapping = new_mapping[prop]['properties']
    mapping['_all'] = {'analyzer': 'encoded_index_analyzer', 'auto_boost': False}
    return mapping


def run(app, collections=None, dry_run=False):
    root = app.root_factory(app)
    if not dry_run:
        es = app.registry[ELASTIC_SEARCH]

    if not collections:
        collections = ['meta'] + root.by_item_type.keys()

    for collection_name in collections:
        if collection_name == 'meta':
            doc_type = 'meta'
            mapping = META_MAPPING
        else:
            doc_type = 'basic'
            collection = root.by_item_type[collection_name]
            mapping = collection_mapping(collection)

        if mapping is None:
            continue  # Testing collections
        if dry_run:
            print json.dumps(
                sorted_dict({collection_name: {doc_type: mapping}}), indent=4)
            continue

        try:
            es.create_index(collection_name, index_settings(collection_name))
        except IndexAlreadyExistsError:
            es.delete_index(collection_name)
            es.create_index(collection_name, index_settings(collection_name))

        es.put_mapping(collection_name, doc_type, {doc_type: mapping})
        es.refresh(collection_name)


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
