"""\
Run this to upgrade the site.

Examples

To update on the production server:

    %(prog)s production.ini

For the development.ini you must supply the paster app name:

    %(prog)s development.ini --app-name app

"""
from contextlib import contextmanager
import logging

EPILOG = __doc__

logger = logging.getLogger(__name__)


DEFAULT_COLLECTIONS = [
    'antibody_lot',
    'biosample',
    'experiment',
    'dataset',
    'platform',
    'treatment',
]


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


def run(testapp, collections):
    from ..storage import DBSession
    with AlternateScope(DBSession) as scope:
        if not collections:
            collections = DEFAULT_COLLECTIONS
        root = testapp.app.root_factory(testapp.app)
        for collection_name in collections:
            collection = root[collection_name]
            count = 0
            errors = 0
            logger.info('Upgrading %s', collection_name)
            for uuid in collection:
                count += 1
                with scope.change():
                    try:
                        testapp.patch_json('/%s' % uuid, {})
                    except Exception:
                        logger.exception('Upgrade failed for: /%s/%s', collection_name, uuid)
                        errors += 1
            logger.info('Upgraded %s: %d (errors: %d)', collection_name, count, errors)


class AlternateScope(object):
    def __init__(self, DBSession):
        self.scope = None
        self._DBSession = DBSession

    def __enter__(self):
        import transaction
        from zope.sqlalchemy.datamanager import join_transaction
        from sqlalchemy.orm.scoping import ScopedRegistry
        self._original_registry = self._DBSession.registry
        self._DBSession.registry = ScopedRegistry(
            self._DBSession.session_factory, self._get_scope)
        self.scope = self
        txn = transaction.begin()
        session = self._DBSession()
        join_transaction(session)
        transaction.manager.free(txn)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._DBSession.registry = self._original_registry
        self.scope = None

    def _get_scope(self):
        return self.scope

    @contextmanager
    def change(self, scope=None):
        previous = self.scope
        self.scope = scope
        yield scope
        self.scope = previous


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Update links and keys", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('--item-type', action='append', help="Item type")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    testapp = internal_app(args.config_uri, args.app_name)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    run(testapp, args.item_type)


if __name__ == '__main__':
    main()
