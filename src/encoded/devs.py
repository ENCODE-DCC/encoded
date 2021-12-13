import argparse
import logging

from pyramid.paster import get_app

from snovault.elasticsearch import create_mapping


EPILOG = __doc__

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Run development servers',
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('config_uri', help="path to configfile")
    parser.add_argument('--init', action="store_true", help="Init database")
    parser.add_argument('--load', action="store_true", help="Load test set")
    args = parser.parse_args()
    logging.basicConfig()
    logging.getLogger('snovault').setLevel(logging.INFO)
    app = get_app(args.config_uri, args.app_name)
    if args.load:
        from encoded.loadxl import load_test_data
        load_test_data(app)
    if args.init:
        create_mapping.run(app)


if __name__ == '__main__':
    main()
