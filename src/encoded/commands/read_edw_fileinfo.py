################
# Console script to read file metadata generated at ENCODE Data Warehouse (EDW)

import sys
import logging
import datetime
import argparse
import copy
from csv import DictReader
from urlparse import urlparse

from pyramid import paster
from webtest import TestApp, AppError

from .. import edw_file

################
# Globals

DEFAULT_INI = 'production.ini'  # Default application initialization file

ENCODE2_ACC = 'wgEncode'         # WARNING: Also in experiment.json and edw_file.py
ENCODE2_PROP = 'encode2_dbxrefs' # WARNING: Also in experiment.json

# Schema object names
FILES = 'files'
EXPERIMENTS = 'experiments'
REPLICATES = 'replicates'
DATASETS = 'datasets'

collections= {}  # Cache collections
collection_hashes= {}  # Cache collections
encode2_to_encode3_map = {}     # Map ENCODE 2 wgEncode* accessions to ENCODE 3

verbose = False


################
# Support functions to localize handling of special fields
# e.g. links, datetime

# Some properties in JSON object from collection return nested objects requiring
# pulling desired property (or an additional GET)
# NOTE: It would be good to derive this info from schema

FILE_EMBEDDED_PROPERTIES = {
    'submitted_by': 'email',
    'replicate': 'biological_replicate_number',
}

def format_app_fileinfo(app, file_dict, exclude=None):
    # Handle links and nested propeties
    global verbose
    if verbose:
        sys.stderr.write('Found app file: %s\n' % (file_dict['accession'])) 
    for link_prop, dest_prop in FILE_EMBEDDED_PROPERTIES.iteritems():
        if link_prop in file_dict:
            prop = file_dict[link_prop]
            if type(prop) == dict:
                file_dict[link_prop] = prop[dest_prop]
            elif prop.startswith('/'):
                # Must issue another GET as embedded prop hasn't been expanded
                resp = app.get(prop)
                prop = resp.json[dest_prop]
                # Submitter email returned by test data (should be user dict)
                if type(prop) == dict:
                    file_dict[link_prop] = prop[dest_prop]
                else:
                    file_dict[link_prop] = prop
            else:
                # Seeing submitter email directly in submitted_by field
                # Might be incorrect test data, but handling it for now
                file_dict[link_prop] = prop
        else:
            if link_prop == 'replicate':
                # special handling of replicate -- only numeric field
                file_dict[link_prop] = 0
            else:
                file_dict[link_prop] = edw_file.NA

    # Extract file and dataset accessionsfrom URLs in JSON
    file_dict['accession'] = file_dict['@id'].split('/')[2]
    file_dict['dataset'] = file_dict['dataset'].split('/')[2]

    # Filter out extra fields (not in FILE_INFO_FIELDS, or excluded)
    for prop in file_dict.keys():
        if (prop not in edw_file.FILE_INFO_FIELDS) or (exclude and prop in exclude):
                del file_dict[prop]

    # Assembly can be missing (e.g. for fastQ's)
    if ('assembly' not in file_dict.keys()) and (exclude and 'assembly' not in exclude):
        file_dict['assembly'] = edw_file.NA


def format_reader_fileinfo(file_dict):
    # Convert types when fileinfo read from TSV into strings
    file_dict['replicate'] = int(file_dict['replicate'])


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

def collection_url(collection):
    # Form URL from collection name
    return '/' + collection + '/'


def get_collection(app, collection):
    # GET JSON objects from app as a list
    # NOTE: perhaps limit=all should be default for JSON output
    # and app should hide @graph (provide an iterator)
    global collections
    if collection not in collections:
        url = collection_url(collection)
        resp = app.get(url + '?collection_source=db&limit=all')
        collections[collection] = resp.json['@graph']
    return collections[collection]


def get_collection_hash(app, collection, key):
    # GET JSON objects from app as a hash
    global collection_hashes
    coll_hash_key = collection + '.' + key
    if coll_hash_key not in collection_hashes:
        coll_hash = {}
        coll = get_collection(app, collection)
        for item in coll:
            if item['accession'] == unicode('ENCSR000ADH'):
                pdb.set_trace()
            if unicode(key) in item:
                item_key = item[unicode(key)]
                print item_key
                coll_hash[item_key] = item
        collection_hashes[coll_hash_key] = coll_hash


################
def get_encode2_accessions(app, encode3_acc):
    # Get ENCODE 2 accessions (or None)
    url = collection_url(EXPERIMENTS) + encode3_acc
    if verbose:
        print "EXPERIMENT: ", encode3_acc
    resp = app.get(url).maybe_follow()
    if ENCODE2_PROP in resp.json:
        return resp.json[ENCODE2_PROP]
    return None


def get_phase(fileinfo, app):
    # Determine phase of file (ENCODE 2 or ENCODE 3)
    acc = get_encode2_accession(app, fileinfo['dataset'])
    if acc is not None:
        return edw_file.ENCODE_PHASE_2
    return edw_file.ENCODE_PHASE_3


def get_encode2_to_encode3_map(app):
    # Map ENCODE2 experiment accession to ENCODE3
    global encode2_to_encode3_map
    if len(encode2_to_encode3_map) == 0:
        experiments = get_collection(app, EXPERIMENTS)
        for experiment in experiments:
            #if item['accession'] != unicode('ENCSR000ADH'):
            encode3_acc = experiment['accession']
            encode2_accs = get_encode2_accessions(app, encode3_acc)
            if encode2_accs is not None and len(encode2_accs) > 0:
                for encode2_acc in encode2_accs:
                    encode2_to_encode3_map[encode2_acc] = encode3_acc
    return encode2_to_encode3_map


def get_encode3_accession(app, encode2_acc):
    # Map ENCODE2 experiment accession to ENCODE3
    map = get_encode2_to_encode3_map(app)
    if encode2_acc in map:
        return map[encode2_acc]
    return None


def set_fileinfo_replicate(app, fileinfo):
    # Obtain replicate identifier from open app
    # using experiment accession and replicate numbers
    # Replicate 0 in fileinfo indicates there is none (e.g. pooled data)
    # If non-zero, Create the replicate if it doesn't exist

    # Clone to preserve input
    new_fileinfo = copy.deepcopy(fileinfo)

    # Check for no replicate
    bio_rep_num = fileinfo['replicate']
    # TODO: change replicate representation in filelinfo to int ?
    if (bio_rep_num == 0):
        del new_fileinfo['replicate']
        return new_fileinfo

    # Also trim out irrelevant assembly
    if new_fileinfo['assembly'] == edw_file.NA:
        del new_fileinfo['assembly']

    # Faking technical replicate for now
    tech_rep_num = edw_file.TECHNICAL_REPLICATE_NUM # TODO, needs EDW changes
    # Find experiment id
    experiment = new_fileinfo['dataset']
    url = collection_url(EXPERIMENTS) + experiment
    resp = app.get(url).maybe_follow()
    exp_id = resp.json['@id']

    # Check for existence of replicate

    # GET all replicates
    reps = get_collection(app, REPLICATES)
    rep_id = None
    for rep in reps:
        if rep['experiment'].rfind(exp_id) != -1 and \
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
        global verbose
        if verbose:
            sys.stderr.write('....POST replicate %d for experiment %s\n' % (bio_rep_num, experiment))
        url = collection_url(REPLICATES)
        resp = app.post_json(url, rep)
        if verbose:
            print resp
        # WARNING: ad-hoc char conversion here
        rep_id = resp.json[unicode('@graph')][0][unicode('@id')]

    # Populate link to replicate, and clone to preserve input
    new_fileinfo['replicate'] = str(rep_id)
    return new_fileinfo


def set_fileinfo_experiment(app, fileinfo):
    # Convert ENCODE2 experiment to ENCODE3
    acc = fileinfo['dataset']
    if (acc.startswith(ENCODE2_ACC)):
        encode3_acc = get_encode3_accession(app, acc)
        if encode3_acc:
            fileinfo['dataset'] = encode3_acc


def get_app_fileinfo(app, full=True, limit=0, exclude=None,
                     phase=edw_file.ENCODE_PHASE_ALL):
    # Get file info from encoded web application
    # Return list of fileinfo dictionaries
    rows = get_collection(app, FILES)
    app_files = []
    for row in rows:
        if full:
            if phase != edw_file.ENCODE_PHASE_ALL:
                if get_phase(row, app) != phase:
                    continue
            format_app_fileinfo(app, row, exclude=exclude)
            app_files.append(row)
        else:
            app_files.append(row['accession'])
        limit -= 1
        if limit == 0:
            break
    return app_files


def get_app_filelist(app, limit=0, phase=edw_file.ENCODE_PHASE_ALL):
    # Get list of file accessions from web app
    return get_app_fileinfo(app, full=False, limit=limit, phase=phase)


def get_new_filelist_from_lists(app_accs, edw_accs):
    # Find 'new' file accessions: files in EDW having experiment accesion 
    #   but missing in app
    new_accs = []
    for accession in edw_accs:
        if accession not in app_accs:
            new_accs.append(accession)
    return new_accs


def get_new_filelist(app, edw, phase=edw_file.ENCODE_PHASE_ALL):
    # Find 'new' accessions: files in EDW having experiment accesion 
    #   but missing in app
    edw_accs = edw_file.get_edw_filelist(edw, phase=phase)
    app_accs = get_app_filelist(app, phase=phase)
    return get_new_filelist_from_lists(app_accs, edw_accs)


def get_new_fileinfo(app, edw, phase=edw_file.ENCODE_PHASE_ALL):
    # Find 'new' files: files in EDW having experiment accession 
    #   but missing in app
    edw_files = edw_file.get_edw_fileinfo(edw, phase=phase)
    app_filelist = get_app_fileinfo(app, phase=phase)

    edw_dict = { d['accession']: d for d in edw_files }
    app_dict = { d['accession']: d for d in app_files }
    new_files = []
    experiments = get_collection(app, EXPERIMENTS)
    for acc in edw_dict.keys():
        if acc not in app_dict:
            # special handling of accession -- need to lookup ENCODE 3 
            #   accession at encoded for ENCODE 2 accession from EDW
            new_file = edw_dict[acc]
            set_fileinfo_experiment(app, new_file)
            new_files.append(new_file)
    return new_files


def post_fileinfo(app, fileinfo):
    # POST file info dictionary to open app

    global verbose
    if verbose:
        sys.stderr.write('....POST file: %s\n' % (fileinfo['accession']))
    # Replace replicate number (bio_rep) with URL for replicate
    # (may require creating one)
    accession = fileinfo['accession']
    try:
        post_fileinfo = set_fileinfo_replicate(app, fileinfo)
    except AppError as e:
        logging.warning('Failed POST File %s: Replicate error\n%s', accession, e)
        return
    url = collection_url(FILES)
    resp = app.post_json(url, post_fileinfo, expect_errors=True)
    if verbose:
        print resp
    if resp.status_int == 409:
        logging.warning('Failed POST File %s: File already exists', accession)
    elif resp.status_int < 200 or resp.status_int >= 400:
        logging.warning('Failed POST File %s\n%s', accession, resp)
    else:
        sys.stderr.write('Successful POST File: %s\n' % (accession))


def put_fileinfo(app, fileinfo):
    # PUT changed file info to open app

    global verbose
    if verbose:
        sys.stderr.write('....PUT file: %s\n' % (fileinfo['accession']))
    accession = fileinfo['accession']
    try:
        put_fileinfo = set_fileinfo_replicate(app, fileinfo)
        url = collection_url(FILES) + accession
        resp = app.put_json(url, put_fileinfo)
        if verbose:
            print resp
        sys.stderr.write('Successful PUT File %s\n', (accession))
    except AppError as e:
        logging.warning('Failed PUT File %s\n%s', accession, e)


################
# Main functions

def show_edw_fileinfo(edw, full=True, limit=None, experiment=True, 
                      phase=edw_file.ENCODE_PHASE_ALL):
    # Read info from file tables at EDW.
    # Format as TSV file with columns from 'encoded' File JSON schema
    if (full):
        sys.stderr.write('Showing ENCODE %s files\n' % phase)
        edw_files = edw_file.get_edw_fileinfo(edw, limit=limit, phase=phase,
                                              experiment=experiment)
        edw_file.dump_fileinfo(edw_files)
    else:
        sys.stderr.write('Showing ENCODE %s file accessions\n' % phase)
        edw_accs = edw_file.get_edw_filelist(edw, limit=limit, phase=phase,
                                             experiment=experiment)
        edw_file.dump_filelist(edw_accs)


def show_app_fileinfo(app, limit=0, phase=edw_file.ENCODE_PHASE_ALL):
    # Read info from file tables at EDW.
    # Write TSV file from list of application file info
    sys.stderr.write('Exporting file info\n')
    app_files = get_app_fileinfo(app, limit=limit, phase=phase)
    edw_file.dump_fileinfo(app_files)


def show_new_fileinfo(app, edw, full=True, phase=edw_file.ENCODE_PHASE_ALL):
    # Show 'new' files: files in EDW having experiment accesion 

    if (full):
        sys.stderr.write('Showing new ENCODE %s files '
                         '(at EDW but not in app)\n' % (phase))
        new_files = get_new_fileinfo(app, edw, phase=phase)
        edw_file.dump_fileinfo(new_files)
    else:
        sys.stderr.write('List new ENCODE %s file accessions '
                         '(at EDW but not in app)\n' % (phase))
        new_accs = get_new_filelist(app, edw, phase=phase)
        edw_file.dump_filelist(new_accs)


def post_app_fileinfo(input_file, app):
    # POST files from input file to app
    sys.stderr.write('Importing file info from %s to app via POST\n' % (input_file))
    with open(input_file, 'rb') as f:
        reader = DictReader(f, delimiter='\t')
        for fileinfo in reader:
            format_reader_fileinfo(fileinfo)
            post_fileinfo(app, fileinfo)


def modify_app_fileinfo(input_file, app):
    # PUT changed file info from input file to app
    sys.stderr.write('Updating file info from %s to app\n' % (input_file))
    with open(input_file, 'rb') as f:
        reader = DictReader(f, delimiter='\t')
        for fileinfo in reader:
            put_fileinfo(app, fileinfo)

def convert_fileinfo(input_file, app):
    # Convert ENCODE2 accessions in input file to ENCODE3 
    sys.stderr.write('Converting ENCODE2 file info in %s to ENCODE3\n' % (input_file))
    with open(input_file, 'rb') as f:
        reader = DictReader(f, delimiter='\t')
        app_files = []
        for fileinfo in reader:
            format_reader_fileinfo(fileinfo)
            set_fileinfo_experiment(app, fileinfo)
            app_files.append(fileinfo)
    edw_file.dump_fileinfo(app_files)


def sync_app_fileinfo(app, edw, phase=edw_file.ENCODE_PHASE_ALL):
    # POST all new files from EDW to app
    sys.stderr.write('Importing new file info for ENCODE %s to app\n' % 
                     (phase))
    # TODO: log imported files
    new_files = get_new_fileinfo(app, edw, phase=phase)
    for fileinfo in new_files:
        post_fileinfo(app, fileinfo)


def show_diff_fileinfo(app, edw, exclude=None, detailed=False,
                       phase=edw_file.ENCODE_PHASE_ALL):
    # Show differences between EDW experiment files and files in app
    sys.stderr.write('Comparing file info for ENCODE %s files at EDW with app\n'
                      % (phase))
    edw_files = edw_file.get_edw_fileinfo(edw, experiment=True,
                                          exclude=exclude, phase=phase)
    edw_dict = { d['accession']: d for d in edw_files }
    app_files = get_app_fileinfo(app, exclude=exclude, phase=phase)
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

    # file-based
    group.add_argument('-i', '--import_file',
                       help='import to app from TSV file')

    # TODO:  Enable this code once tested
    #group.add_argument('-I', '--import_all_new', action='store_true',
                       #help='import all new files from EDW to app; '
                            #'use -n to view new file info before import')

    group.add_argument('-m', '--modify_file',
                   help='modify files in app using info in TSV file')
    group.add_argument('-23', '--convert_file',
                   help='convert ENCODE2 entries in TSV file to ENCODE3')

    group.add_argument('-c', '--compare_summary', action='store_true', 
                   help='summary compare of experiment files in EDW with app')
    group.add_argument('-C', '--compare_full', action='store_true',
                   help='detailed compare of experiment files in EDW with app')
    group.add_argument('-e', '--export', action='store_true',
                   help='export file info from app')
    group.add_argument('-n', '--new_list', action='store_true',
                   help='list new file accession: in EDW not in app')
    group.add_argument('-N', '--new_files', action='store_true',
                   help='show new files: in EDW not in app')
    group.add_argument('-w', '--edw_list', action='store_true',
                   help='show file accessions at EDW')
    group.add_argument('-W', '--edw_files', action='store_true',
                   help='show file info at EDW')

    # modifiers
    parser.add_argument('-l', '--limit', type=int, default=0,
                   help='limit number of files to show; '
                        'for EDW, most recently submitted are listed first')
    parser.add_argument('-P', '--phase',  
                            choices=[edw_file.ENCODE_PHASE_2, 
                                     edw_file.ENCODE_PHASE_3, 
                                     edw_file.ENCODE_PHASE_ALL], 
                            default=edw_file.ENCODE_PHASE_ALL,
                    help='restrict EDW files by ENCODE phase accs '
                         '(default %s)' % edw_file.ENCODE_PHASE_ALL),
    parser.add_argument('-exclude', '--exclude_props', nargs='+', 
                        help='for -c and -C, ignore excluded properties')
    #parser.add_argument('-x', '--experiment', action='store_true',
                    #help='for EDW, show only files having experiment accession')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose mode')
    parser.add_argument('-d', '--data_host', default=None,
                        help='data warehouse host (default from my.cnf)')
    parser.add_argument('-a', '--application', default=DEFAULT_INI,
                    help='application url or .ini (default %s)' % DEFAULT_INI)
    parser.add_argument('--username', '-u', default='',
                    help='HTTP username (access_key_id) or import user')
    parser.add_argument('--password', '-p', default='',
                        help='HTTP password (secret_access_key)')
            
    args = parser.parse_args()

    global verbose
    verbose = args.verbose
    edw_file.verbose = verbose

    # CAUTION: fragile code here.  Should restructure with subcommands or
    #   custom action

    # init encoded app
    if args.export or args.modify_file or args.import_file or args.convert_file or\
        args.new_list or args.new_files \
        or args.compare_full or args.compare_summary:
            app = make_app(args.application, args.username, args.password)

    # open connection to EDW
    if args.edw_files or args.edw_list or args.new_list or args.new_files or \
        args.compare_full or args.compare_summary:
            edw = edw_file.make_edw(args.data_host)

    # pick a task
    if args.import_file:
        post_app_fileinfo(args.import_file, app)

    #elif args.import_all_new:
        #sync_app_fileinfo(args.phase, args.data_host, app)

    elif args.modify_file:
        modify_app_fileinfo(args.modify_file, app)

    elif args.convert_file:
        convert_fileinfo(args.convert_file, app)

    elif args.export:
        show_app_fileinfo(app, limit=args.limit, phase=args.phase)

    elif args.new_list:
        show_new_fileinfo(app, edw, full=False, phase=args.phase)

    elif args.new_files:
        show_new_fileinfo(app, edw, full=True, phase=args.phase)

    elif args.compare_summary:
        show_diff_fileinfo(app, edw, detailed=False, 
                           exclude=args.exclude_props, phase=args.phase)

    elif args.compare_full:
        show_diff_fileinfo(app, edw, detailed=True, 
                           exclude=args.exclude_props, phase=args.phase)

    elif args.edw_list:
        show_edw_fileinfo(edw, full=False, limit=args.limit, phase=args.phase)

    elif args.edw_files:
        show_edw_fileinfo(edw, limit=args.limit, phase=args.phase)

    else:
        parser.print_usage()
        sys.exit(1)

if __name__ == '__main__':
    main()
