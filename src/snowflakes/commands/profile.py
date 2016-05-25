"""\
Profile a url

Examples

To run on the production server:

    %(prog)s production.ini "/experiments/ENCSR000ADI/?format=json&datastore=database"

For the development.ini you must supply the paster app name:

    %(prog)s development.ini --app-name app "/experiments/ENCSR000ADI/?format=json&datastore=database"

"""
import logging
import cProfile
import pstats

EPILOG = __doc__

logger = logging.getLogger(__name__)


def internal_app(configfile, app_name=None, username=None, accept_json=True):
    from webtest import TestApp
    from pyramid import paster
    app = paster.get_app(configfile, app_name)
    if not username:
        username = 'IMPORT'
    environ = {
        'REMOTE_USER': username,
    }
    if accept_json:
        environ['HTTP_ACCEPT'] = 'application/json'
    return TestApp(app, environ)


def parse_restriction(value):
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def run(testapp, method, path, data, warm_ups, filename, sortby, stats, callers, callees, response_body):
    method = method.lower()
    if method == 'get':
        fn = lambda: testapp.get(path)
    else:
        fn = lambda: getattr(testapp, method)(path, data, content_type='application/json')
    for n in range(warm_ups):
        res = fn()
        logger.info('Warm up %d:\n\t%s', n + 1, res.headers['X-Stats'].replace('&', '\n\t'))
    pr = cProfile.Profile()
    pr.enable()
    res = fn()
    pr.disable()
    logger.info('Run:\n\t%s', res.headers['X-Stats'].replace('&', '\n\t'))
    if response_body:
        print(res.text)
    pr.create_stats()
    ps = pstats.Stats(pr).sort_stats(sortby)
    if stats:
        ps.print_stats(*(parse_restriction(r) for r in stats))
    if callers:
        ps.print_callers(*(parse_restriction(r) for r in callers))
    if callees:
        ps.print_callees(*(parse_restriction(r) for r in callees))
    if filename is not None:
        ps.dump_stats(filename)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Update links and keys", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--warm-ups', default=1, type=int, help="Warm ups")
    parser.add_argument('--filename', help="profile filename")
    parser.add_argument('--stat', default=[], action='append', help="print_stats restrictions")
    parser.add_argument('--caller', default=[], action='append', help="print_callers restrictions")
    parser.add_argument('--callee', default=[], action='append', help="print_callees restrictions")
    parser.add_argument('--sortby', default='time', help="profile sortby")
    parser.add_argument('--response-body', action='store_true', help="Print response body")
    parser.add_argument('--method', default='GET', help="HTTP method")
    parser.add_argument('--data', help="json request body")
    parser.add_argument(
        '--html', dest='accept_json', action='store_false', default=True,
        help="Don't set 'Accept: application/json'")
    parser.add_argument(
        '--username', '-u', default='TEST', help="User uuid/email")
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('config_uri', help="path to configfile")
    parser.add_argument('path', help="path to profile")
    args = parser.parse_args()

    logging.basicConfig()
    testapp = internal_app(args.config_uri, args.app_name, args.username, args.accept_json)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('snovault').setLevel(logging.DEBUG)

    run(testapp, args.method, args.path, args.data, args.warm_ups, args.filename, args.sortby,
        args.stat, args.caller, args.callee, args.response_body)


if __name__ == '__main__':
    main()
