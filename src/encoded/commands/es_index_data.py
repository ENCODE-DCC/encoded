from pyramid.paster import get_app
from ..indexing import ELASTIC_SEARCH
import logging
from webtest import TestApp

index = 'encoded'

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

        DOCTYPE = collection_name

        # try creating index, if it exists already delete it and create it
        counter = 0
        for count, uuid in enumerate(collection):
            try:
                res = testapp.get('/%s/@@index-data' % uuid).maybe_follow()
            except:
                print "Object is not found - " + str(uuid)
            else:
                document = res.json
                es.index(index, DOCTYPE, document, str(uuid))
                counter = counter + 1
                if counter % 50 == 0:
                    es.flush(index)
                    log.info('Indexing %s %d', collection_name, counter)
        es.refresh(index)


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
