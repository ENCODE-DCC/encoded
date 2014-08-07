"""\
Run this when links or keys are changed in the schema.

Examples

To update all keys and rels on the production server:

    %(prog)s production.ini

For the development.ini you must supply the paster app name:

    %(prog)s development.ini --app-name app

"""
import logging
import transaction
from pyramid.paster import get_app
from pyramid.traversal import resource_path

EPILOG = __doc__

logger = logging.getLogger(__name__)

DEFAULT_COLLECTIONS = [
    'file',
]


def run(app, collections=None):
    root = app.root_factory(app)
    if not collections:
        collections = DEFAULT_COLLECTIONS
    for collection_name in collections:
        collection = root[collection_name]
        collection_path = resource_path(collection)
        updated = 0
        for count, item in enumerate(collection.itervalues()):
            path = resource_path(item)
            keys_add, keys_remove = item.update_keys()
            update = False
            if keys_add or keys_remove:
                logger.debug('Updated keys: %s' % path)
                update = True

            rels_add, rels_remove = item.update_rels()
            if rels_add or rels_remove:
                logger.debug('Updated links: %s' % path)
                update = True
            if update:
                updated += 1
        logger.info('Collection %s: Updated %d of %d.' %
            (collection_path, updated, count))


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Update links and keys", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--item-type', action='append', help="Item type")
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('--abort', action='store_true', help="Rollback transaction")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    app = get_app(args.config_uri, args.app_name)
    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    raised = False
    try:
        run(app, args.item_type)
    except:
        raised = True
        raise
    finally:
        if raised or args.abort:
            transaction.abort()
            logger.info('Rolled back.')
        else:
            transaction.commit()


if __name__ == '__main__':
    main()
