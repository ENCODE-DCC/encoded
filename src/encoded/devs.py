"""\
Examples
For the development.ini you must supply the paster app name:
    %(prog)s development.ini --app-name app --init --clear
"""
from pkg_resources import resource_filename
from pyramid.paster import get_app, get_appsettings
from multiprocessing import Process, set_start_method

from snovault.elasticsearch import create_mapping

import atexit
import logging
import os.path
import select
import shutil
import sys
import pdb
import subprocess
import time


EPILOG = __doc__

logger = logging.getLogger(__name__)


def print_to_terminal(stdout):
    while True:
        printed = False
        for line in iter(stdout.readline, b''):
            if line:
                sys.stdout.write(line.decode('utf-8'))
                printed = True
        if not printed:
            time.sleep(0.1)

def nginx_server_process(prefix='', echo=False):
    args = [
        os.path.join(prefix, 'nginx'),
        '-c', resource_filename('snovault', 'nginx-dev.conf'),
        '-g', 'daemon off; pid /dev/null;'
    ]
    process = subprocess.Popen(
        args,
        close_fds=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if not echo:
        process.stdout.close()

    if echo:
        print('Started: http://localhost:8000')

    return process

def main():

    import argparse
    parser = argparse.ArgumentParser(
        description="Run development servers", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('config_uri', help="path to configfile")
    parser.add_argument('--clear', action="store_true", help="Clear existing data")
    parser.add_argument('--init', action="store_true", help="Init database")
    parser.add_argument('--load', action="store_true", help="Load test set")
    parser.add_argument('--datadir', default='/tmp/snovault', help="path to datadir")
    args = parser.parse_args()

    appsettings = get_appsettings(args.config_uri, name='app')


    logging.basicConfig()
    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('snovault').setLevel(logging.INFO)
    import os

    app = get_app(args.config_uri, args.app_name)

    if args.load:
        from encoded.loadxl import load_test_data
        load_test_data(app)

    if args.init:
        create_mapping.run(app)



if __name__ == '__main__':
    main()
