"""\
Example.

    %(prog)s production.ini

"""

from webtest import TestApp
from snovault import STORAGE
from snovault.elasticsearch import ELASTIC_SEARCH
import atexit
import datetime
import elasticsearch.exceptions
import json
import logging
import os
import psycopg2
import select
import signal
import socket
import sqlalchemy.exc
import sys
import threading
import time
from urllib.parse import parse_qsl

log = logging.getLogger(__name__)

EPILOG = __doc__
DEFAULT_TIMEOUT = 60
PY2 = sys.version_info[0] == 2

# We need this because of MVCC visibility.
# See slide 9 at http://momjian.us/main/writings/pgsql/mvcc.pdf
# https://devcenter.heroku.com/articles/postgresql-concurrency


def run(testapp, timeout=DEFAULT_TIMEOUT, dry_run=False, path='/index', control=None, update_status=None):
    assert update_status is not None

    timestamp = datetime.datetime.now().isoformat()
    update_status(
        status='connecting',
        timestamp=timestamp,
        timeout=timeout,
    )

    # Make sure elasticsearch is up before trying to index.
    if path == '/index_file':
        es = testapp.app.registry['snp_search']
    else:
        es = testapp.app.registry[ELASTIC_SEARCH]
    es.info()

    max_xid = 0
    DBSession = testapp.app.registry[STORAGE].write.DBSession
    engine = DBSession.bind  # DBSession.bind is configured by app init
    # noqa http://docs.sqlalchemy.org/en/latest/faq.html#how-do-i-get-at-the-raw-dbapi-connection-when-using-an-engine
    connection = engine.pool.unique_connection()
    try:
        connection.detach()
        conn = connection.connection
        conn.autocommit = True
        conn.set_session(readonly=True)
        sockets = [conn]
        if control is not None:
            sockets.append(control)
        recovery = None
        listening = False
        with conn.cursor() as cursor:
            while True:
                if not listening:
                    # cannot execute LISTEN during recovery
                    cursor.execute("""SELECT pg_is_in_recovery();""")
                    recovery, = cursor.fetchone()
                    if not recovery:
                        # http://initd.org/psycopg/docs/advanced.html#asynchronous-notifications
                        cursor.execute("""LISTEN "snovault.transaction";""")
                        log.debug("Listener connected")
                        listening = True

                cursor.execute("""SELECT txid_current_snapshot();""")
                snapshot, = cursor.fetchone()
                timestamp = datetime.datetime.now().isoformat()
                update_status(
                    listening=listening,
                    recovery=recovery,
                    snapshot=snapshot,
                    status='indexing',
                    timestamp=timestamp,
                    max_xid=max_xid,
                )

                try:
                    res = testapp.post_json(path, {
                        'record': True,
                        'dry_run': dry_run,
                        'recovery': recovery,
                    })
                except Exception as e:
                    timestamp = datetime.datetime.now().isoformat()
                    log.exception('index failed at max xid: %d', max_xid)
                    update_status(error={
                        'error': repr(e),
                        'max_xid': max_xid,
                        'timestamp': timestamp,
                    })
                else:
                    timestamp = datetime.datetime.now().isoformat()
                    result = res.json
                    result['stats'] = {
                        k: int(v) for k, v in parse_qsl(
                            res.headers.get('X-Stats', ''))
                    }
                    result['timestamp'] = timestamp
                    update_status(last_result=result)
                    if result.get('indexed', 0):
                        update_status(result=result)
                        log.info(result)

                update_status(
                    status='waiting',
                    timestamp=timestamp,
                    max_xid=max_xid,
                )
                # Wait on notifcation
                readable, writable, err = select.select(sockets, [], sockets, timeout)

                if err:
                    raise Exception('Socket error')

                if control in readable:
                    command = control.recv(1)
                    log.debug('received command: %r', command)
                    if not command:
                        # Other end shutdown
                        return

                if conn in readable:
                    conn.poll()

                while conn.notifies:
                    notify = conn.notifies.pop()
                    xid = int(notify.payload)
                    max_xid = max(max_xid, xid)
                    log.debug('NOTIFY %s, %s', notify.channel, notify.payload)

    finally:
        connection.close()


class ErrorHandlingThread(threading.Thread):
    if PY2:
        @property
        def _kwargs(self):
            return self._Thread__kwargs

        @property
        def _args(self):
            return self._Thread__args

        @property
        def _target(self):
            return self._Thread__target

    def run(self):
        timeout = self._kwargs.get('timeout', DEFAULT_TIMEOUT)
        update_status = self._kwargs['update_status']
        control = self._kwargs['control']
        while True:
            try:
                self._target(*self._args, **self._kwargs)
            except (psycopg2.OperationalError, sqlalchemy.exc.OperationalError, elasticsearch.exceptions.ConnectionError) as e:
                # Handle database restart
                log.warning('Database not there, maybe starting up: %r', e)
                timestamp = datetime.datetime.now().isoformat()
                update_status(
                    timestamp=timestamp,
                    status='sleeping',
                    error={'error': repr(e), 'timestamp': timestamp},
                )

                readable, _, _ = select.select([control], [], [], timeout)
                if control in readable:
                    command = control.recv(1)
                    log.debug('received command: %r', command)
                    if not command:
                        # Other end shutdown
                        return

                log.debug('sleeping')
                time.sleep(timeout)
                continue
            except Exception:
                # Unfortunately mod_wsgi does not restart immediately
                log.exception('Exception in listener, restarting process at next request.')
                os.kill(os.getpid(), signal.SIGINT)
            break


def composite(loader, global_conf, **settings):
    listener = None

    # Register before testapp creation.
    @atexit.register
    def join_listener():
        if listener:
            log.debug('joining listening thread')
            listener.join()

    path = settings.get('path', '/index')

    # Composite app is used so we can load the main app
    app_name = settings.get('app', None)
    app = loader.get_app(app_name, global_conf=global_conf)
    username = settings.get('username', 'IMPORT')
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': username,
    }
    testapp = TestApp(app, environ)

    # Use sockets to integrate with select
    controller, control = socket.socketpair()

    timestamp = datetime.datetime.now().isoformat()
    status_holder = {
        'status': {
            'status': 'starting listener',
            'started': timestamp,
            'errors': [],
            'results': [],
        },
    }

    def update_status(error=None, result=None, indexed=None, **kw):
        # Setting a value in a dictionary is atomic
        status = status_holder['status'].copy()
        status.update(**kw)
        if error is not None:
            status['errors'] = [error] + status['errors'][:9]
        if result is not None:
            status['results'] = [result] + status['results'][:9]
        status_holder['status'] = status

    kwargs = {
        'testapp': testapp,
        'control': control,
        'update_status': update_status,
        'path': path,
    }
    if 'timeout' in settings:
        kwargs['timeout'] = float(settings['timeout'])

    listener = ErrorHandlingThread(target=run, name='listener', kwargs=kwargs)
    listener.daemon = True
    log.debug('starting listener')
    listener.start()

    # Register before testapp creation.
    @atexit.register
    def shutdown_listener():
        log.debug('shutting down listening thread')
        control  # Prevent early gc
        controller.shutdown(socket.SHUT_RDWR)

    def status_app(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'application/json')]
        start_response(status, response_headers)
        return [json.dumps(status_holder['status'])]

    return status_app


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
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument(
        '--username', '-u', default='INDEXER', help="Import username")
    parser.add_argument(
        '--dry-run', action='store_true', help="Don't post to ES, just print")
    parser.add_argument(
        '-v', '--verbose', action='store_true', help="Print debug level logging")
    parser.add_argument(
        '--poll-interval', type=int, default=DEFAULT_TIMEOUT,
        help="Poll interval between notifications")
    parser.add_argument(
        '--path', default='/index',
        help="Path of indexing view (/index or /index_file)")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    testapp = internal_app(args.config_uri, args.app_name, args.username)

    # Loading app will have configured from config file. Reconfigure here:
    if args.verbose or args.dry_run:
        logging.getLogger('snovault').setLevel(logging.DEBUG)

    return run(testapp, args.poll_interval, args.dry_run, args.path)


if __name__ == '__main__':
    main()
