"""\
Examples

To check all pages on the production server:

    %(prog)s production.ini

For the development.ini you must supply the paster app name:

    %(prog)s development.ini --app-name app

"""
import json
import logging
from future.utils import itervalues
from pyramid.traversal import resource_path

EPILOG = __doc__

logger = logging.getLogger(__name__)

def check_path(testapp, path):
    try:
        res = testapp.get(path, status='*').maybe_follow(status='*')
    except Exception:
        logger.exception('Render failed: %s', path)
        return False
    if res.status_int != 200:
        logger.error('Render failed (%s): %s', res.status, path)
        script = res.html.find('script', **{'data-prop-name': 'context'})
        if script is not None:
            context = json.loads(script.text)
            if 'detail' in context:
                logger.debug(context['detail'])
            else:
                logger.debug(json.dumps(context, indent=4))
        return False
    return True


def run(testapp, collections=None):
    app = testapp.app
    root = app.root_factory(app)
    if not collections:
        collections = root.by_item_type.keys()
        check_path(testapp, '/')
    for collection_name in collections:
        collection = root[collection_name]
        collection_path = resource_path(collection, '')
        check_path(testapp, collection_path)
        failed = 0
        for count, item in enumerate(itervalues(collection)):
            path = resource_path(item, '')
            if not check_path(testapp, path):
                failed += 1
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
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('--username', '-u', default='TEST',
        help="User uuid/email")
    parser.add_argument('config_uri', help="path to configfile")
    parser.add_argument('path', nargs='*', help="path to test")
    args = parser.parse_args()

    logging.basicConfig()
    testapp = internal_app(args.config_uri, args.app_name, args.username)
    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('snowflakes').setLevel(logging.DEBUG)

    if args.path:
        failed = 0
        for path in args.path:
            if not check_path(testapp, path):
                failed += 1
        if failed:
            logger.info('Paths: %d of %d failed to render.',
                failed, len(args.path))
        else:
            logger.info('Paths: all %d rendered ok', len(args.path))
    else:
        run(testapp, args.item_type)


if __name__ == '__main__':
    main()
