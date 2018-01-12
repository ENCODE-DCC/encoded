from pyramid.paster import get_app
from elasticsearch import RequestError
import logging
import json

from snovault.elasticsearch.interfaces import ELASTIC_SEARCH


EPILOG = __doc__

log = logging.getLogger(__name__)

index = 'annotations'
doc_type = 'default'


def json_from_path(path, default=None):
    if path is None:
        return default
    return json.load(open(path))

def index_settings():
    return {
        'index': {
            'number_of_shards': 1,
<<<<<<< HEAD
        }, 
=======
            'max_result_window': 99999
        },
>>>>>>> master
        'analysis.analyzer': 'standard'
    }


def run(app):
    registry = app.registry
    es = app.registry[ELASTIC_SEARCH]
    try:
        es.indices.create(index=index, body=index_settings())
    except RequestError:
        es.indices.delete(index=index)
        es.indices.create(index=index, body=index_settings())

    mapping = {
        'properties': {
            'suggest': {
                'type': 'completion',
            }
        }
    }
    try:
        es.indices.put_mapping(
            index=index,
            doc_type=doc_type,
            body={doc_type: mapping}
        )
    except:
        print("Could not create mapping for the collection %s", doc_type)
    else:
        es.indices.refresh(index=index)

    # bulk index of annotations
    annotations = json_from_path(registry.settings.get('annotations_path'), {})
    try:
        es.bulk(index=index, body=annotations, refresh=True, request_timeout=30)
    except:
        print("Unable index the annotations")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Index annotations in Elasticsearch", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    app = get_app(args.config_uri, args.app_name)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    return run(app)


if __name__ == '__main__':
    main()
