"""\
The inpath is the path to either:

  - a zip file or directory containing single sheet xlsx/tsv/csv files named
    after the object type, e.g. experiment.xlsx, antibody_lot.tsv

  - a single Excel workbook with worksheets named after the object types.

Examples.

To load the initial data:

    %(prog)s --attach $DIR_HOLDING_ATTACHMENTS \\
        --attach $DIR_HOLDING_SPREADSHHETS \\
        ../documents-export.zip dev-masterdata.ini

To make updates from a single tsv file

    %(prog)s --username ACCESS_KEY_ID --password SECRET_ACCESS_KEY \\
        --patch ../updates/ http://localhost:6543

"""
from webtest import TestApp
from urllib.parse import urlparse
from .. import loadxl
import logging
import os.path

EPILOG = __doc__


def basic_auth(username, password):
    from base64 import b64encode
    from pyramid.compat import ascii_native_
    return 'Basic ' + ascii_native_(b64encode(('%s:%s' % (username, password)).encode('utf-8')))


def remote_app(base, username='', password=''):
    environ = {'HTTP_ACCEPT': 'application/json'}
    if username:
        environ['HTTP_AUTHORIZATION'] = basic_auth(username, password)

    return TestApp(base, environ)


def internal_app(configfile, app_name=None, username=''):
    from pyramid import paster
    app = paster.get_app(configfile, app_name)
    if not username:
        username = 'IMPORT'
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': username,
    }
    return TestApp(app, environ)


def run(testapp, filename, docsdir, method, item_type, test=False):
    name, ext = os.path.splitext(filename)
    if ext in ['', '.xlsx']:
        source = loadxl.read_single_sheet(filename, item_type)
    else:
        source = loadxl.read_single_sheet(filename)
    pipeline = loadxl.get_pipeline(testapp, docsdir, test, item_type, method=method)
    loadxl.process(loadxl.combine(source, pipeline))


def main():
    # https://github.com/gawel/WSGIProxy2/pull/3 (and change to WebTest)
    from wsgiproxy.proxies import ALLOWED_METHODS
    if 'PATCH' not in ALLOWED_METHODS:
        ALLOWED_METHODS.append('PATCH')

    import argparse
    parser = argparse.ArgumentParser(
        description="Import data", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--test-only', action='store_true')
    parser.add_argument('--item-type', help="Item type")
    parser.add_argument('--post', dest='method', action='store_const',
        const="POST", help="Create new data")
    parser.add_argument('--put', dest='method', action='store_const',
        const="PUT", help="Replace existing data")
    parser.add_argument('--patch', dest='method', action='store_const',
        const="PATCH", help="Patch existing data")
    parser.add_argument('--username', '-u', default='',
        help="HTTP username (access_key_id) or import user uuid/email")
    parser.add_argument('--password', '-p', default='',
        help="HTTP password (secret_access_key)")
    parser.add_argument('--attach', '-a', action='append', default=[],
        help="Directory to search for attachments")
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('inpath',
        help="input zip file/directory of excel/csv/tsv sheets.")
    parser.add_argument('url',
        help="either the url to the application or path to configfile")
    args = parser.parse_args()

    logging.basicConfig()

    url = urlparse(args.url)
    if urlparse(args.url).scheme in ('http', 'https'):
        base = url.scheme + '://' + url.netloc
        username = args.username
        password = args.password
        if url.username:
            base = url.scheme + '://' + url.netloc.split('@', 1)[1]
            assert not args.username
            username = url.username
            if url.password:
                assert not args.password
                password = url.password
        testapp = remote_app(base, username, password)
    else:
        testapp = internal_app(args.url, args.app_name, args.username)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('snovault').setLevel(logging.INFO)
    logging.getLogger('wsgi').setLevel(logging.WARNING)

    if args.method:
        run(testapp, args.inpath, args.attach, args.method, args.item_type, args.test_only)
    else:
        loadxl.load_all(testapp, args.inpath, args.attach, args.test_only)


if __name__ == '__main__':
    main()
