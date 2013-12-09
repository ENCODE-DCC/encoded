"""\
Examples

To check all pages on the production server:

    %(prog)s production.ini

For the development.ini you must supply the paster app name:

    %(prog)s development.ini --app app

"""
import logging
from pyramid.traversal import resource_path

EPILOG = __doc__

logger = logging.getLogger(__name__)


def run(testapp, collections=None):
    app = testapp.app
    root = app.root_factory(app)
    if not collections:
        collections = root.by_item_type.keys()
    for collection_name in collections:
        collection = root[collection_name]
        collection_path = resource_path(collection, '')
        failed = 0
        for count, item in enumerate(collection.itervalues()):
            path = resource_path(item, '')
            res = testapp.get(path, status='*')
            if res.status_int != 200:
                failed += 1
                logger.error('Render failed (%s): %s', res.status, path)
        if failed:
            logger.info('Collection %s: %d of %d failed to render.',
                collection_path, failed, count)
        else:
            logger.info('Collection %s: all %d rendered ok',
                collection_path, count)


def internal_app(configfile, app_name=None, username='TEST', accept='text/html'):
    from pyramid import paster
    from webtest import TestApp
    app = paster.get_app(configfile, app_name)
    environ = {
        'HTTP_ACCEPT': accept,
        'REMOTE_USER': username,
    }
    return TestApp(app, environ)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Check rendering of items", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--item-type', action='append', help="Item type")
    parser.add_argument('--app', help="Pyramid app name in configfile")
    parser.add_argument('--username', '-u', default='TEST',
        help="User uuid/email")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    testapp = internal_app(args.config_uri, args.app, args.username)
    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    run(testapp, args.item_type)


if __name__ == '__main__':
    main()
