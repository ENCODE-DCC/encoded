from pyramid.paster import get_app
import logging
from webtest import TestApp

index = 'encoded_file'
collection_name = 'file'
types = ['narrowPeak', 'broadPeak']

EPILOG = __doc__


def run(app, record=False):
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'INDEXER',
    }
    testapp = TestApp(app, environ)
    testapp.post_json('/file_index', {'last_xmin': None})


def main():
    ''' Indexes Bed files are loaded to elasticsearch '''

    import argparse
    parser = argparse.ArgumentParser(
        description="Index data in Elastic Search", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--record', default=False, action='store_true', help="Record the xmin in ES meta")
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    app = get_app(args.config_uri, args.app_name)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)
    return run(app, args.record)


if __name__ == '__main__':
    main()
