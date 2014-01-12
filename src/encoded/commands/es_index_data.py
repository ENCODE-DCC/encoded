from pyramid.paster import get_app
from pyramid.security import principals_allowed_by_permission
from ..indexing import ELASTIC_SEARCH
import logging
from webtest import TestApp

DOCTYPE = 'basic'

EPILOG = __doc__

log = logging.getLogger(__name__)


def run(app, collections=None):
    root = app.root_factory(app)
    es = app.registry[ELASTIC_SEARCH]
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'IMPORT',
    }
    testapp = TestApp(app, environ)

    if not collections:
        collections = root.by_item_type.keys()

    for collection_name in collections:
        collection = root.by_item_type[collection_name]
        if collection.schema is None:
            continue

        # try creating index, if it exists already delete it and create it
        counter = 0
        for count, item in enumerate(collection.itervalues()):
            links = {}
            
            # links for the item
            for link in item.links:
                links[link] = []
                if type(item.links[link]) is list:
                    for l in item.links[link]:
                        links[link].append(str(l.uuid))
                else:
                    links[link].append(str(item.links[link].uuid))

            # Get keys for the item
            keys = []
            for key in item.model.unique_keys:
                keys.append(key.value)

            # Principals for the item
            principals = {}
            _principals = principals_allowed_by_permission(item, 'edit')

            if item.name_key is None:
                item_path = '/' + root.by_item_type[collection_name].__name__ \
                    + '/' + str(item.uuid) + '/'
            else:
                item_path = '/' + root.by_item_type[collection_name].__name__ \
                    + '/' + str(item.properties[item.name_key]) + '/'
            try:
                item_json = testapp.get(item_path, headers={'Accept': 'application/json'}, status=200)
            except Exception as e:
                print e
            else:
                document_id = str(item_json.json['uuid'])
                try:
                    unembedded_item_json = testapp.get(item_path + '?embed=false', headers={'Accept': 'application/json'}, status=200)
                except Exception as e:
                    print e
                else:
                    document = {
                        'embedded': item_json.json,
                        'unembedded': unembedded_item_json.json,
                        'links': links,
                        'keys': keys
                    }
                    es.index(collection_name, DOCTYPE, document, document_id)
                    counter = counter + 1
                    if counter % 50 == 0:
                        es.flush(collection_name)
                        log.info('Indexing %s %d', collection_name, counter)

        es.refresh(collection_name)


def main():
    ''' Indexes app data loaded to elasticsearch '''

    import argparse
    parser = argparse.ArgumentParser(
        description="Index data in Elastic Search", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--item-type', action='append', help="Item type")
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    app = get_app(args.config_uri, args.app_name)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)
    return run(app, args.item_type)


if __name__ == '__main__':
    main()
