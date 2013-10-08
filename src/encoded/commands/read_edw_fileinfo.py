################
# Console script to read file metadata generated at ENCODE Data Warehouse (EDW)

import sys
import logging
import datetime
import argparse
from csv import DictReader, DictWriter
from urlparse import urlparse

from pyramid import paster
from webtest import TestApp, AppError

from .. import edw_file

################
# Globals

DEFAULT_INI = 'edw.ini'  # Default application initialization file

FILES_URL = '/files/'
EXPERIMENTS_URL = '/experiments/'
REPLICATES_URL = '/replicates/'

ENCODE_PHASE_2 = '2'
ENCODE_PHASE_3 = '3'
ENCODE_PHASE_ALL = 'all'


################
# Support functions to localize handling of special fields
# e.g. links, datetime

# Some properties in JSON object from collection are links requiring a
# further GET.
# NOTE: It would be good to derive this info from schema

# Some properties in JSON object from collection return nested objects requiring
# pulling desired property
FILE_NESTED_PROPERTIES = {
    'replicate': 'biological_replicate_number',
    'submitted_by': 'email',
}

def format_app_fileinfo(file_dict, app):
    # Handle links and nested propeties
    for link_prop, dest_prop in FILE_NESTED_PROPERTIES.iteritems():
        if link_prop in file_dict:
            file_dict[link_prop] = file_dict[link_prop][dest_prop]
        else:
            file_dict[link_prop] = edw_file.NA

    # extract file and dataset accessionsfrom URLs in JSON
    # NOTE: shouldn't 'accession' property of file JSON be the file's accession ?
    # it's currently the dataset accession
    file_dict['accession'] = file_dict['@id'].split('/')[2]
    file_dict['dataset'] = file_dict['dataset'].split('/')[2]

    # Filter out extra fields (not in FILE_INFO_FIELDS)
    for prop in file_dict.keys():
        if prop not in edw_file.FILE_INFO_FIELDS:
            del file_dict[prop]

    # Assembly can be missing
    if 'assembly' not in file_dict.keys():
        file_dict['assembly'] = edw_file.NA


################
# Initialization

# CAUTION: hacked in from import-data script

IMPORT_USER = 'IMPORT'

def basic_auth(username, password):
    from base64 import b64encode
    return 'Basic ' + b64encode('%s:%s' % (username, password))

def remote_app(base, username='', password=''):
    environ = {'HTTP_ACCEPT': 'application/json'}
    if username:
        environ['HTTP_AUTHORIZATION'] = basic_auth(username, password)
    else:
        environ['REMOTE_USER'] = IMPORT_USER
    return TestApp(base, environ)


def internal_app(configfile, username=''):
    app = paster.get_app(configfile)
    if not username:
        username = IMPORT_USER
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': username,
    }
    return TestApp(app, environ)
# END CAUTION


def make_app(application, username, password):
    # Configure test app pyramid .ini file or use application URL
    logging.basicConfig()
    sys.stderr.write('Using encoded app: %s\n' % application)

    # CAUTION: pasted from import-data script
    url = urlparse(application)
    if url.scheme in ('http', 'https'):
        base = url.scheme + '://' + url.netloc
        if url.username:
            base = url.scheme + '://' + url.netloc.split('@', 1)[1]
            username = url.username
            if url.password:
                password = url.password
        app = remote_app(base, username, password)
    else:
        app = internal_app(application, username)
    # END CAUTION
    return app

################
# Utility classes and functions

def get_collection(app, url):
    # GET JSON objects from app as a list of JSON objects
    # NOTE: perhaps limit=all should be default for JSON output
    # and app should hide @graph (provide an iterator)
    resp = app.get(url + '?limit=all')
    return resp.json['@graph']


def get_phase(fileinfo, app):
    # Determine phase of file (ENCODE 2 or ENCODE 3)
    resp = app.get(fileinfo['dataset']).maybe_follow()
    if len(resp.json['encode2_dbxrefs']) == 0:
        return ENCODE_PHASE_3
    else:
        return ENCODE_PHASE_2


def get_app_fileinfo(phase, app, limit=0):
    # Get file info from encoded web application
    # Return list of fileinfo dictionaries
    rows = get_collection(app, FILES_URL)
    app_files = []
    for row in rows:
        if phase != ENCODE_PHASE_ALL:
            if get_phase(row, app) != phase:
                continue
        format_app_fileinfo(row, app)
        app_files.append(row)
        limit -= 1
        if limit == 0:
            break
    return app_files


def get_new_fileinfo(phase, data_host, app):
    # Find 'new' files: files in EDW having experiment accesion 
    #   but missing in app
    edw_files = edw_file.get_edw_fileinfo(phase, data_host, experiment=True)
    edw_dict = { d['accession']: d for d in edw_files }
    app_files = get_app_fileinfo(phase, application, user, password)
    app_dict = { d['accession']: d for d in app_files }
    new_files = []
    for accession in edw_dict.keys():
        if accession not in app_dict:
            new_files.append(edw_dict[accession])
    return new_files


def set_fileinfo_replicate(app, fileinfo):
    # Obtain replicate identifier from open app
    # using experiment accession and replicate numbers
    # Create the replicate if it doesn't exist

    # Find experiment id
    experiment = fileinfo['dataset']
    resp = app.get(EXPERIMENTS_URL + experiment).maybe_follow()
    exp_id = resp.json['@id']

    # Check for existence of replicate
    reps = get_collection(app, REPLICATES_URL)
    bio_rep_num = int(fileinfo['replicate'])
    tech_rep_num = int(edw_file.TECHNICAL_REPLICATE_NUM) # TODO, needs EDW changes
    rep_id = None
    for rep in reps:
        if rep['experiment'] == exp_id and \
            rep['biological_replicate_number'] == bio_rep_num and \
            rep['technical_replicate_number'] == tech_rep_num:
                rep_id = rep['@id']
                break

    if rep_id is None:
        # Create a replicate
        rep = { 
            'experiment': exp_id,
            'biological_replicate_number': bio_rep_num,
            'technical_replicate_number': tech_rep_num
        }
        resp = app.post_json(REPLICATES_URL, rep)
        rep_id = resp.json['@id']

    # Populate link to replicate
    fileinfo['replicate'] = rep_id


def post_fileinfo(app, fileinfo):
    # POST file info dictionary to open app

    # Take care of replicate; may require creating one
    accession = fileinfo['accession']
    try:
        set_fileinfo_replicate(app, fileinfo)
    except AppError as e:
        logging.warning('Failed POST File %s: Replicate error\n%s', accession, e)
        return
    resp = app.post_json(FILES_URL, fileinfo, expect_errors=True)
    if resp.status_int == 409:
        logging.warning('Failed POST File %s: File already exists', accession)
    elif resp.status_int < 200 or resp.status_int >= 400:
        logging.warning('Failed POST File %s\n%s', accession, resp)


def put_fileinfo(app, fileinfo):
    # PUT changed file info to open app

    accession = fileinfo['accession']
    try:
        set_fileinfo_replicate(app, fileinfo)
        app.put_json(FILES_URL + accession, fileinfo)
    except AppError as e:
        logging.warning('Failed PUT File %s\n%s', accession, e)


################
# Main functions

def show_edw_fileinfo(phase, data_host, limit=None, experiment=None):
    # Read info from file tables at EDW.
    # Format as TSV file with columns from 'encoded' File JSON schema
    sys.stderr.write('Showing ENCODE %s file info\n' % phase)
    edw_files = edw_file.get_edw_fileinfo(phase, data_host, limit, experiment)
    edw_file.dump_fileinfo(edw_files)


def show_app_fileinfo(phase, app, limit):
    # Read info from file tables at EDW.
    # Write TSV file from list of application file info
    sys.stderr.write('Exporting file info\n')
    app_files = get_app_fileinfo(phase, app, limit)
    edw_file.dump_fileinfo(app_files)


def show_new_fileinfo(phase, data_host, app):
    # Show 'new' files: files in EDW having experiment accesion 
    sys.stderr.write('Showing new ENCODE %s files (at EDW but not in app)\n' % 
                     (phase))
    new_files = get_new_fileinfo(phase, data_host, app)
    edw_file.dump_fileinfo(new_files)


def write_app_fileinfo(input_file, app):
    # POST files from input file to app
    sys.stderr.write('Importing file info from %s to app\n' % (input_file))
    with open(input_file, 'rb') as f:
        reader = DictReader(f, delimiter='\t')
        for fileinfo in reader:
            post_fileinfo(app, fileinfo)


def modify_app_fileinfo(input_file, app):
    # PUT changed file info from input file to app
    sys.stderr.write('Updating file info from %s to app\n' % (input_file))
    with open(input_file, 'rb') as f:
        reader = DictReader(f, delimiter='\t')
        for fileinfo in reader:
            put_fileinfo(app, fileinfo)


def sync_app_fileinfo(phase, data_host, app):
    # POST all new files from EDW to app
    sys.stderr.write('Importing new file info for ENCODE %s from %s to app\n' % 
                     (phase, data_host))
    # TODO: log imported files
    new_files = get_new_fileinfo(phase, data_host, app)
    for fileinfo in new_files:
        post_fileinfo(app, fileinfo)


def show_diff_fileinfo(phase, data_host, app, detailed=False):
    # Show differences between EDW experiment files and files in app
    sys.stderr.write('Comparing file info for ENCODE %s files at EDW with app\n'
                      % (phase))
    edw_files = edw_file.get_edw_fileinfo(phase, data_host, experiment=True)
    edw_dict = { d['accession']: d for d in edw_files }
    app_files = get_app_fileinfo(phase, app)
    app_dict = { d['accession']: d for d in app_files }

    # Inventory files
    edw_only = []
    app_only = []
    same = []
    diff_accessions = []

    for accession in sorted(edw_dict.keys()):
        if accession not in app_dict:
            edw_only.append(edw_dict[accession])
        else:
            set_edw = set(edw_dict[accession].items())
            set_app = set(app_dict[accession].items())
            if len(set_edw ^ set_app) == 0:
                same.append(edw_dict[accession])
            else:
                diff_accessions.append(accession)

    # APP-only files
    for accession in sorted(app_dict.keys()):
        if accession not in edw_dict:
            app_only.append(app_dict[accession])

    # Dump out
    if (detailed):
        edw_file.dump_fileinfo(edw_only, typeField='EDW_ONLY')
        edw_file.dump_fileinfo(app_only, typeField='APP_ONLY', header=False)

        #print len(diff_accessions), 'different files'
        for accession in diff_accessions:
            edw_diff_files = [ edw_dict[accession] ]
            app_diff_files = [ app_dict[accession] ]
            edw_file.dump_fileinfo(edw_diff_files, typeField='EDW_DIFF', header=False)
            edw_file.dump_fileinfo(app_diff_files, typeField='APP_DIFF', header=False)

        edw_file.dump_fileinfo(same, typeField='SAME', header=False)
    else:
        sys.stdout.write('EDW_ONLY: %d\n' % len(edw_only))
        sys.stdout.write('APP_ONLY: %d\n' % len(app_only))
        sys.stdout.write('SAME: %d\n' % len(same))
        sys.stdout.write('DIFFERENT: %d\n' % len(diff_accessions))


################
# Main

def main():
    parser = argparse.ArgumentParser(
        description='Show ENCODE file info; import from EDW to encoded app')

    group = parser.add_mutually_exclusive_group()

    # functions
    group.add_argument('-i', '--import_file',
                       help='import to app from TSV file')

    # TODO:  Enable this code once tested
    #group.add_argument('-I', '--import_all_new', action='store_true',
                       #help='import all new files from EDW to app; '
                            #'use -n to view new file info before import')

    group.add_argument('-m', '--modify_file',
                   help='modify files in app using info in TSV file')
    group.add_argument('-c', '--compare_summary', action='store_true',
                   help='summary compare of experiment files in EDW with app')
    group.add_argument('-C', '--compare_full', action='store_true',
                   help='detailed compare of experiment files in EDW with app')
    group.add_argument('-e', '--export', action='store_true',
                   help='export file info from app')
    group.add_argument('-n', '--new', action='store_true',
                   help='show new files: in EDW not in app')
    group.add_argument('-w', '--edw', action='store_true',
                   help='show file info at EDW')

    # modifiers
    parser.add_argument('-l', '--limit', type=int, default=0,
                   help='limit number of files to show; '
                          'for EDW, most recently submitted are listed first')
    parser.add_argument('-P', '--phase',  
                choices=[ENCODE_PHASE_2, ENCODE_PHASE_3, ENCODE_PHASE_ALL], 
                default=ENCODE_PHASE_ALL,
                    help='limit EDW files by ENCODE phase accs (default %s)' %
                            ENCODE_PHASE_ALL),
    parser.add_argument('-x', '--experiment', action='store_true',
                    help='for EDW, show only files having experiment accession')
    parser.add_argument('-d', '--data_host',
                        help='data warehouse host (default from ./edw.cfg)')
    parser.add_argument('-a', '--application', default=DEFAULT_INI,
                    help='application url or .ini (default %s)' % DEFAULT_INI)
    parser.add_argument('--username', '-u', default='',
                    help='HTTP username (access_key_id) or import user')
    parser.add_argument('--password', '-p', default='',
                        help='HTTP password (secret_access_key)')
            
    args = parser.parse_args()

    if not args.edw:
        app = make_app(args.application, args.username, args.password)

    if args.import_file:
        write_app_fileinfo(args.import_file, app)

    #elif args.import_all_new:
        #sync_app_fileinfo(args.phase, args.data_host, app)

    elif args.modify_file:
        modify_app_fileinfo(args.modify_file, app)

    elif args.export:
        show_app_fileinfo(args.phase, app, args.limit)

    elif args.new:
        show_new_fileinfo(args.phase, app)

    elif args.compare_summary:
        show_diff_fileinfo(args.phase, args.data_host, app, detailed=False)

    elif args.compare_full:
        show_diff_fileinfo(args.phase, args.data_host, app, detailed=True)

    else:
        show_edw_fileinfo(args.phase, args.data_host, args.limit, args.experiment)

if __name__ == '__main__':
    main()
