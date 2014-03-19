"""\
Example.

    %(prog)s production.ini

"""

from pyramid.settings import asbool
from webtest import TestApp
from ..storage import DBSession

import atexit
import datetime
import json
import logging
import os
import psycopg2
import select
import signal
import socket
import sqlalchemy.exc
import threading
import time
import urlparse

log = logging.getLogger(__name__)

EPILOG = __doc__
DEFAULT_TIMEOUT = 60

# We need this because of MVCC visibility.
# See slide 9 at http://momjian.us/main/writings/pgsql/mvcc.pdf
# https://devcenter.heroku.com/articles/postgresql-concurrency

def run(testapp, timeout=DEFAULT_TIMEOUT, dry_run=False, control=None, status_holder=None):
    # Setting a value in a dictionary is atomic
    if status_holder is None:
        status_holder = {'status': {}}

    timestamp = datetime.datetime.now().isoformat()
    status = status_holder['status'].copy()
    status['status'] = 'connecting'
    status['timestamp'] = timestamp
    status['timeout'] = timeout
    status, status_holder['status'] = status, status.copy()

    post_data = {'record': True}
    if dry_run:
        post_data['dry_run'] = True

    max_xid = 0
    engine = DBSession.bind  # DBSession.bind is configured by app init
    # http://docs.sqlalchemy.org/en/latest/faq.html#how-do-i-get-at-the-raw-dbapi-connection-when-using-an-engine
    connection = engine.pool.unique_connection()
    try:
        connection.detach()
        conn = connection.connection
        conn.autocommit = True
        with conn.cursor() as cursor:
            sockets = [conn]
            if control is not None:
                sockets.append(control)
            # http://initd.org/psycopg/docs/advanced.html#asynchronous-notifications
            cursor.execute("""LISTEN "encoded.transaction";""")
            log.debug("Listener connected")
            timestamp = datetime.datetime.now().isoformat()
            status['connected'] = timestamp
            while True:
                timestamp = datetime.datetime.now().isoformat()
                status['status'] = 'indexing'
                status['timestamp'] = timestamp
                status['max_xid'] = max_xid
                status, status_holder['status'] = status, status.copy()

                try:
                    res = testapp.post_json('/index', post_data)
                except Exception:
                    timestamp = datetime.datetime.now().isoformat()
                    log.exception('index failed at max xid: %d', max_xid)
                    status['last_indexing_error_max_xid'] = max_xid
                    status['last_indexing_error_timestamp'] = timestamp
                else:
                    timestamp = datetime.datetime.now().isoformat()
                    log.debug(res.json)
                    status['last_result'] = res.json
                    status['last_stats'] = {
                        k: int(v) for k, v in urlparse.parse_qsl(
                            res.headers.get('X-Stats', ''))
                    }
                    if res.json.get('count', 0):
                        status['last_indexing_result'] = status['last_result']
                        status['last_indexing_stats'] = status['last_stats']
                        status['last_indexing_timestamp'] = timestamp

                status['status'] = 'listening'
                status['timestamp'] = timestamp
                status['max_xid'] = max_xid
                status, status_holder['status'] = status, status.copy()

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
    def run(self):
        timeout = self._Thread__kwargs.get('timeout', DEFAULT_TIMEOUT)
        status_holder =  self._Thread__kwargs.get('status_holder')
        if status_holder is None:
            status_holder = {'status': {}}
        status = status_holder['status'].copy()
        while True:
            try:
                self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
            except (psycopg2.OperationalError, sqlalchemy.exc.OperationalError) as e:
                # Handle database restart
                log.exception('Database went away')
                timestamp = datetime.datetime.now().isoformat()
                status = status_holder['status'].copy()
                status['status'] = 'sleeping'
                status['timestamp'] = timestamp
                status['last_db_error_timestamp'] = timestamp
                status_holder['status'] = status
                log.debug('sleeping')
                time.sleep(timeout)
                continue
            except Exception as e:
                # Unfortunately mod_wsgi does not restart immediately
                log.exception('Exception in listener, restarting process at next request.')
                os.kill(os.getpid(), signal.SIGINT)
            break


def composite(loader, global_conf, **settings):
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
        },
    }

    kwargs = {
        'testapp': testapp,
        'control': control,
        'status_holder': status_holder,
    }
    if 'timeout' in settings:
        kwargs['timeout'] = float(settings['timeout'])

    listener = ErrorHandlingThread(target=run, name='listener', kwargs=kwargs)
    listener.daemon = True
    log.debug('starting listener')
    listener.start()

    @atexit.register
    def shutdown_listener():
        log.debug('shutting down listening thread')
        control  # Prevent early gc 
        controller.shutdown(socket.SHUT_RDWR)
        listener.join()


    def status_app(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type','application/json')]
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
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    testapp = internal_app(args.config_uri, args.app_name, args.username)

    # Loading app will have configured from config file. Reconfigure here:
    if args.verbose or args.dry_run:
        logging.getLogger('encoded').setLevel(logging.DEBUG)

    return run(testapp, args.poll_interval, args.dry_run)


if __name__ == '__main__':
    main()
