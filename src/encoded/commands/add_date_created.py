"""\
Run this to upgrade the site.

Examples

To update on the production server:

    %(prog)s production.ini

For the development.ini you must supply the paster app name:

    %(prog)s development.ini --app app

"""
from pyramid.traversal import resource_path
import logging
import pytz

pacific = pytz.timezone('US/Pacific')

EPILOG = __doc__

logger = logging.getLogger(__name__)



def internal_app(configfile, app_name=None, username=None):
    from webtest import TestApp
    from pyramid import paster
    app = paster.get_app(configfile, app_name)
    if not username:
        username = 'IMPORT'
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': username,
    }
    return TestApp(app, environ)


def run(testapp, collections=None, dry_run=False):
    root = testapp.app.root_factory(testapp.app)
    if not collections:
        collections = root.by_item_type.keys()
    for collection_name in collections:
        collection = root[collection_name]
        if collection.schema is None or 'date_created' not in collection.schema.get('properties', ()):
            logger.info('Skipped %s', collection_name)
            continue
        count = 0
        errors = 0
        logger.info('Upgrading %s', collection_name)
        for uuid, item in collection.iteritems():
            history = item.model.data[''].history
            first_propsheet = history[0]
            if 'date_created' in first_propsheet.properties:
                continue
            last_propsheet = history[-1]
            if len(history) != 1 and 'date_created' in last_propsheet.properties:
                for i, propsheet in enumerate(history):
                    if 'date_created' in propsheet.properties:
                        break
                if propsheet is last_propsheet or \
                        propsheet.properties['date_created'] != last_propsheet.properties['date_created'] or \
                        propsheet.transaction.data['userid'] != "remoteuser.IMPORT":
                    continue
                wrong_date = last_propsheet.properties['date_created']
                logger.info('Overwriting wrong date_created (%s) for %s', wrong_date, path)
            date_created = first_propsheet.transaction.timezone.replace(tzinfo=pacific)
            count += 1
            if dry_run:
                continue
            try:
                testapp.patch_json('/%s' % uuid, {'date_created': date_created.isoformat()})
            except Exception:
                logger.exception('Upgrade failed for: %s', path)
                errors += 1
        logger.info('Upgraded %s: %d (errors: %d)', collection_name, count, errors)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Fix date_created", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--item-type', action='append', help="Item type")
    parser.add_argument('--app', help="Pyramid app name in configfile")
    parser.add_argument(
        '--dry-run', action='store_true', help="Don't post to ES, just print")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    testapp = internal_app(args.config_uri, args.app)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)
    run(testapp, args.item_type, args.dry_run)


if __name__ == '__main__':
    main()
