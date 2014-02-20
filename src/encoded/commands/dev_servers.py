"""\
Examples
For the development.ini you must supply the paster app name:

    %(prog)s development.ini --app app --init --clear

"""
from pyramid.paster import get_app

import atexit
import logging
import os.path
import select
import shutil

EPILOG = __doc__

logger = logging.getLogger(__name__)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Run development servers", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app', help="Pyramid app name in configfile")
    parser.add_argument('config_uri', help="path to configfile")
    parser.add_argument('--clear', action="store_true", help="Clear existing data")
    parser.add_argument('--init', action="store_true", help="Init database")
    parser.add_argument('--load', action="store_true", help="Load test set")
    parser.add_argument('--datadir', default='/tmp/encoded', help="path to datadir")
    args = parser.parse_args()

    logging.basicConfig()
    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    from encoded.tests import elasticsearch_fixture, postgresql_fixture
    from encoded.commands import create_mapping
    datadir = os.path.abspath(args.datadir)
    pgdata = os.path.join(datadir, 'pgdata')
    esdata = os.path.join(datadir, 'esdata')
    if args.clear:
        for dirname in [pgdata, esdata]:
            if os.path.exists(dirname):
                shutil.rmtree(dirname)
    if args.init:
        postgresql_fixture.initdb(pgdata, echo=True)

    postgres = postgresql_fixture.server_process(pgdata, echo=True)
    elasticsearch = elasticsearch_fixture.server_process(esdata, echo=True)
    processes = [postgres, elasticsearch]

    @atexit.register
    def cleanup_process():
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                for line in process.stdout:
                    print line,
            except IOError:
                pass
            process.wait()

    if args.init:
        app = get_app(args.config_uri, args.app)
        create_mapping.run(app)

    if args.load:
        from webtest import TestApp
        environ = {
            'HTTP_ACCEPT': 'application/json',
            'REMOTE_USER': 'TEST',
        }
        testapp = TestApp(app, environ)

        from encoded.loadxl import load_all
        from pkg_resources import resource_filename
        inserts = resource_filename('encoded', 'tests/data/inserts/')
        docsdir = [resource_filename('encoded', 'tests/data/documents/')]
        load_all(testapp, inserts, docsdir)

    print 'Started. ^C to exit.'

    stdouts = [p.stdout for p in processes]

    # Ugly should probably use threads instead
    while True:
        readable, writable, err = select.select(stdouts, [], stdouts, 5)
        for stdout in readable:
            for line in iter(stdout.readline, ''):
                print line,
        if err:
            for stdout in err:
                for line in iter(stdout.readline, ''):
                    print line,
            break

if __name__ == '__main__':
    main()
