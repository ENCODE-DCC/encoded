"""\
Run this to upgrade the site.

Examples

To update on the production server:

    %(prog)s production.ini

For the development.ini you must supply the paster app name:

    %(prog)s development.ini --app-name app

"""
import logging
import transaction

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


def run(testapp):
    root = testapp.app.root_factory(testapp.app)
    for collection_name in ['biosample', 'experiment', 'dataset', 'antibody_characterization', 'biosample_characterization', 'rnai_characterization']
        collection = root[collection_name]
        count = 0
        errors = 0
        logger.info('Upgrading %s', collection_name)
        for uuid in collection:
            count += 1
            try:
                testapp.patch_json('/%s' % uuid, {})
            except Exception:
                logger.exception('Upgrade failed for: /%s/%s', collection_name, uuid)
                errors += 1
        logger.info('Upgraded %s: %d (errors: %d)', collection_name, count, errors)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Update links and keys", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('--abort', action='store_true', help="Rollback transaction")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    testapp = internal_app(args.config_uri, args.app_name)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    run(testapp)


if __name__ == '__main__':
    main()
