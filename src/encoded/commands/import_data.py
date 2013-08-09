"""\
The inpath is the path to either:

  - a zip file or directory containing single sheet xlsx/tsv/csv files named
    after the object type, e.g. experiment.xlsx, antibody_lot.tsv

  - a single Excel workbook with worksheets named after the object types.

Examples.

To load the initial data:

    %(prog)s --attach ../dccMetadataImport/data/documents/ \\
        --attach ../dccMetadataImport/data/ENCODE3docs/ \\
        ../documents-export.zip dev-masterdata.ini

To load updates from a directory of xlsx/tsv tils

    %(prog)s --username ACCESS_KEY_ID --password SECRET_ACCESS_KEY \\
        --update ../updates/ http://localhost:6543

"""
from webtest import TestApp
from urlparse import urlparse
from .. import loadxl
import logging

EPILOG = __doc__

def basic_auth(username, password):
    from base64 import b64encode
    return 'Basic ' + b64encode('%s:%s' % (username, password))


def remote_app(base, username='', password=''):
    environ = {'HTTP_ACCEPT': 'application/json'}
    if username:
        environ['HTTP_AUTHORIZATION'] = basic_auth(username, password)

    return TestApp(base, environ)


def internal_app(configfile, username=''):
    from pyramid import paster
    app = paster.get_app(configfile)
    if not username:
        username = 'IMPORT'
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': username,
    }    
    return TestApp(app, environ)


def run(url):
    pass


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Import data", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--test-only', '-t', action='store_true')
    parser.add_argument('--update', action='store_true',
        help="Update existing data instead of creating new data")
    parser.add_argument('--username', '-u', default='',
        help="HTTP username (access_key_id) or import user uuid/email")
    parser.add_argument('--password', '-p', default='',
        help="HTTP password (secret_access_key)")
    parser.add_argument('--attach', '-a', action='append', default=[],
        help="Directory to search for attachments")
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
        testapp = internal_app(args.url, args.username)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.INFO)
    logging.getLogger('wsgi').setLevel(logging.WARNING)

    if args.update:
        loadxl.update_all(testapp, args.inpath, args.attach, args.test_only)
    else:
        loadxl.load_all(testapp, args.inpath, args.attach, args.test_only)


if __name__ == '__main__':
    main()
