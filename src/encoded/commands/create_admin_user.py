from pyramid.paster import get_app
import logging
from webtest import TestApp

EPILOG = __doc__


def run(app, first_name, last_name, email, lab):
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': 'TEST',
    }
    testapp = TestApp(app, environ)
    testapp.post_json('/user', {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'lab': lab,
        'groups': ['admin']
    })


def main():
    ''' Creates an admin user '''

    import argparse
    parser = argparse.ArgumentParser(
        description="Creates an admin user", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--first-name', default='Admin', help="First name")
    parser.add_argument('--last-name', default='Test', help="Last name")
    parser.add_argument('--email', default='admin_test@example.org', help="E-mail")
    parser.add_argument('--lab', default='/labs/j-michael-cherry/', help="Lab")
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    options = {
        'embed_cache.capacity': '5000',
        'indexer': 'true',
    }
    app = get_app(args.config_uri, args.app_name, options)

    logging.getLogger('encoded').setLevel(logging.DEBUG)
    return run(app, args.first_name, args.last_name, args.email, args.lab)


if __name__ == '__main__':
    main()
