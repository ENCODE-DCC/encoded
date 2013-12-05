"""\
Example.

    %(prog)s production.ini

"""

from ..storage import DBSession
import json
import logging
import select
log = logging.getLogger(__name__)

EPILOG = __doc__

# We need this because of MVCC visibility.
# See slide 9 at http://momjian.us/main/writings/pgsql/mvcc.pdf

def run(testapp, poll_interval=60, dry_run=False):
    max_xid = 0

    engine = DBSession.bind  # DBSession.bind is configured by app init
    # http://docs.sqlalchemy.org/en/latest/faq.html#HowdoIgetattherawDBAPIconnectionwhenusinganEngine
    connection = engine.pool.unique_connection()  # DBSession.bind is configured by app init
    connection.detach()
    conn = connection.connection
    conn.autocommit = True
    cursor = conn.cursor()
    try:
        # http://initd.org/psycopg/docs/advanced.html#asynchronous-notifications
        cursor.execute("""LISTEN "encoded.transaction";""")
        while True:
            if any(select.select([conn], [], [], poll_interval)):
                conn.poll()

            while conn.notifies:
                notify = conn.notifies.pop()
                xid = int(notify.payload)
                max_xid = max(max_xid, xid)
                log.debug('NOTIFY %s, %s' % (notify.channel, notify.payload))

            post_data = {}
            if dry_run:
                post_data['dry_run'] = True

            try:
                res = testapp.post_json('/index', post_data)
            except Exception:
                log.exception('index failed at max xid: %d' % max_xid)
            else:
                log.debug(res.json)

    finally:
        conn.close()


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


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Listen for changes from postgres and index in elasticsearch",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app', help="Pyramid app name in configfile")
    parser.add_argument(
        '--username', '-u', default='INDEXER', help="Import username")
    parser.add_argument(
        '--dry-run', action='store_true', help="Don't post to ES, just print")
    parser.add_argument(
        '-v', '--verbose', action='store_true', help="Print debug level logging")
    parser.add_argument(
        '--poll-interval', type=int, default=60, help="Poll interval between notifications")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    testapp = internal_app(args.config_uri, args.app, args.username)

    # Loading app will have configured from config file. Reconfigure here:
    if args.verbose or args.dry_run:
        logging.getLogger('encoded').setLevel(logging.DEBUG)

    return run(testapp, args.poll_interval, args.dry_run)


if __name__ == '__main__':
    main()
