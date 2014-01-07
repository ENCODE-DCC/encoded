"""\
Example.

To load the initial data:

    %(prog)s production.ini

"""
import sys
import logging
import datetime
import argparse
import copy
import re
from csv import DictReader
from urlparse import urlparse
from operator import itemgetter

from pyramid.paster import get_app
from webtest import TestApp, AppError

from encoded import edw_file

################
# Globals

# Change this when file schema changes
FILE_SCHEMA_VERSION = '1'

DEFAULT_INI = 'production.ini'  # Default application initialization file

ENCODE2_ACC = 'wgEncodeE'  # WARNING: Also in experiment.json and edw_file.py
ENCODE3_ACC = 'ENC'
ENCODE3_EXP_ACC = ENCODE3_ACC + 'SR'  # WARNING: Also in experiment.json
ENCODE2_PROP = 'encode2_dbxrefs' # WARNING: Also in experiment.json

# Schema object names
FILES = 'files'
EXPERIMENTS = 'experiments'
REPLICATES = 'replicates'
DATASETS = 'datasets'
USERS = 'users'

SEARCH_EC2 = '/search/?encode2_dbxrefs='
FILE_PROFILE_URL = '/profiles/file.json'

app_host_name = 'localhost'

EPILOG = __doc__

NO_UPDATE = ['md5sum', 'replicate', 'dataset']
IMPORT_USER = 'IMPORT'

logger = logging.getLogger(__name__)

def convert_edw(app, file_dict):
    ''' converts EDW file structure to encoded object'''

    logger.info('Found EDW file: %s' % (file_dict['accession']))

    # convert time stamp
    valid_time = file_dict['date_created']
    if (type(valid_time) == float):
        file_dict['date_created'] = datetime.datetime.fromtimestamp(
           valid_time).strftime('%Y-%m-%d')
    elif not re.match('\d+-\d+\d+', valid_time):
        logger.error("Invalid time string: %s" % valid_time)
        sys.exit(1)


    if (file_dict['lab_error_message'] or file_dict['edw_error_message'] ):
        file_dict['status'] = 'OBSOLETE'
    else:
        file_dict['status'] = 'CURRENT'

    del file_dict['lab_error_message']
    del file_dict['edw_error_message']
     # hide assembly for fastQ's -- (EDW retains it to represent organism)
    if file_dict['file_format'] in ['fasta', 'fastq']:
        del file_dict['assembly']

    resp = app.get('/users/'+file_dict['submitted_by'],headers={'Accept': 'application/json'}).maybe_follow()
    if not file_dict['submitted_by'] or resp.status_code != 200:
        logger.error('EDW submitter %s cannot be found' % file_dict['submitted_by'])
    else:
        file_dict['submitted_by'] = resp.json['@id']

    try:
        ds_acc = file_dict['dataset']
    except:
        logger.error('EDW file %s has no dataset' % file_dict['accession'])
        ds_acc = None

    if ds_acc:
        ds = get_encode3_experiment(app, ds_acc)
        if not ds:
            logger.error('EDW file %s has a dataset that cannot be found: %s' % (file_dict['accession'], ds_acc))
        else:
            file_dict['dataset'] = ds['@id']
            if ds['dataset_type'] == 'experiment':
                file_dict['replicate'] = find_replicate(ds, file_dict['biological_replicate'], file_dict['technical_replicate'])

    if file_dict.has_key('replicate') and file_dict['replicate']:
        del file_dict['biological_replicate']
        del file_dict['technical_replicate']
            # otherwise we will try tor create the specified one.

    return { i : unicode(j) for i,j in file_dict.items() }


def find_replicate(experiment, bio_rep, tech_rep):

    if (not bio_rep or not tech_rep):
        logger.warn("No replicate specified for experiment")
        return None
    matches = [ rep for rep in experiment['replicates']
      if rep['biological_replicate_number'] == int(bio_rep) and
         rep['technical_replicate_number'] == int(tech_rep)]
    assert(len(matches)<=1)
    if matches:
        return matches[0]['@id']
    else:
        return None


def get_encode2_to_encode3(app):
    # Create and cache list of ENCODE 3 experiments with ENCODE2 accessions
    # Used to map EDW ENCODE 2 accessions to ENCODE3 accession
    global encode2_to_encode3
    global verbose

    if encode2_to_encode3 is not None:
        return encode2_to_encode3
    encode2_to_encode3 = {}
    experiments = get_collection(app, EXPERIMENTS)
    for item in experiments:
        url = item['@id']
        resp = app.get(url).maybe_follow()
        exp = resp.json
        encode3_acc = exp['@id']
        if verbose:
            logger.info('Get experiment (e2-e3): %s' % (encode3_acc))
        encode2_accs = get_encode2_accessions(app, encode3_acc)
        if encode2_accs is not None and len(encode2_accs) > 0:
            for encode2_acc in encode2_accs:
                if encode2_acc in encode2_to_encode3.keys():
                    logger.warning('Multiple ENCODE3 accs for ENCODE2 acc %s,'
                                    ' replacing %s with %s',
                                encode2_acc,
                                encode2_to_encode3[encode2_acc],
                                encode3_acc)
                encode2_to_encode3[encode2_acc] = encode3_acc
    return encode2_to_encode3


def get_encode3_experiment(app, accession):
    # Map ENCODE2 experiment accession to ENCODE3
    # This will fail if EDW references a dataset instead of expt.
    global datasets
    if accession.startswith(ENCODE3_EXP_ACC):
        return exp_or_dataset(app, accession)

    url = SEARCH_EC2 + accession + '&type=experiment'
    #, headers={'Accept': 'application/json'}
    resp = app.get(url).maybe_follow()
    results = resp.json['@graph']
    if not results:
        return None #  are datasets implemented in search yet?
        url = SEARCH_EC2 + accession + '&type=dataset'
        results = resp.json['@graph']

    assert(len(results)==1)
    return app.get(results[0]['@id'],headers={'Accept': 'application/json'}).json


def exp_or_dataset(app, accession):

    url = '/' + accession + '/'
    try:
        resp = app.get(url, headers={'Accept': 'application/json'}).maybe_follow()
    except AppError:
        logger.error("Dataset/Experiment %s could not be found." % accession)
        return None

    if resp.status_code == 200:
        return resp.json
    else:
        return None


def get_missing_filelist_from_lists(app_accs, edw_accs):
    # Find 'new' file accessions: files in EDW having experiment accesion
    #   but missing in app
    new_accs = []
    for accession in edw_accs:
        if accession not in app_accs:
            new_accs.append(accession)
    return new_accs


def get_app_fileinfo(app, phase=edw_file.ENCODE_PHASE_ALL):
    # Get file info from encoded web application
    # Return list of fileinfo dictionaries
    rows = get_collection(app, FILES)
    app_files = []
    for row in sorted(rows, key=itemgetter('accession')):
        url = row['@id']
        resp = app.get(url).maybe_follow()
        fileinfo = resp.json
        # below seems clunky, could search+filter
        if phase != edw_file.ENCODE_PHASE_2:
            if get_phase(app, fileinfo) != phase:
                    continue
        app_files.append(resp.json)
    return app_files


def is_encode2_experiment(app, accession):
    # Does this experiment have ENCODE2 accession
    if accession.startswith(ENCODE2_ACC):
        return True
    if get_encode2_accessions(app, accession) is not None:
        return True
    return False

encode3_to_encode2 = {}    # Cache experiment ENCODE 2 ref lists


def get_encode2_accessions(app, encode3_acc):
    # Get list of ENCODE 2 accessions for this ENCODE 3 experiment(or None)
    global encode3_to_encode2
    if encode3_acc not in encode3_to_encode2:
        logger.info('Get experiment (get e2): %s' % (encode3_acc))
        resp = app.get(encode3_acc).maybe_follow()
        encode3_to_encode2[encode3_acc] = resp.json[ENCODE2_PROP]
    encode2_accs = encode3_to_encode2[encode3_acc]
    if len(encode2_accs) > 0:
        return encode2_accs
    return None




def get_phase(app, fileinfo):
    # Determine phase of file (ENCODE 2 or ENCODE 3)
    if is_encode2_experiment(app, fileinfo['dataset']):
        return edw_file.ENCODE_PHASE_2
    return edw_file.ENCODE_PHASE_3


def create_replicate(app, exp, bio_rep_num, tech_rep_num):

    # create a replicate
    logger.warning("Creating replicate %s %s for %s" % (bio_rep_num, tech_rep_num, exp))
    rep = {
        'experiment': exp,
        'biological_replicate_number': bio_rep_num,
        'technical_replicate_number': tech_rep_num
    }

    logger.info('....POST replicate %d - %d for experiment %s' % (bio_rep_num, tech_rep_num, exp))
    url = collection_url(REPLICATES)
    if not dry_run:

        resp = app.post_json(url, rep)
        logger.info(str(resp))
        rep_id = str(resp.json[unicode('@graph')][0]['@id'])
        return rep_id

    else:
        return "/replicate/new"


def post_fileinfo(app, fileinfo, dry_run=False):
    # POST file info dictionary to open app

    accession = fileinfo['accession']

    logger.info('....POST file: %s' % (accession))

    ds = fileinfo.get('dataset', None)
    dataset = None
    if ds:
        try:
            ds_resp = app.get('/'+ds).maybe_follow()
        except AppError, e:
            logger.error("Refusing to POST file with invalid dataset: %s (%s)" % (ds, e))
            return None
        else:
            dataset = ds_resp.json
    rep = fileinfo.get('replicate', None)
    if ds:
        if dataset and dataset.get('@type', [])[0] == 'dataset':
            # dataset primary files have irrelvant replicate info
            del fileinfo['biological_replicate']
            del fileinfo['technical_replicate']
        elif ( not rep or app.get(rep).maybe_follow().status_code != 200 ):
            # try to create one
            try:
                br = int(fileinfo['biological_replicate'])
                tr = int(fileinfo['technical_replicate'])
                fileinfo['replicate'] = create_replicate(app, ds, br, tr, dry_run)
                del fileinfo['biological_replicate']
                del fileinfo['technical_replicate']
            except ValueError:
                logger.error("Refusing to POST file with confusing replicate ids: %s %s" %
                   (fileinfo['biological_replicate'], fileinfo['technical_replicate']))
                return None
            except KeyError:
                logger.error("Refusing to POST file with missing replicate ids: %s  %s" %
                   (fileinfo['biological_replicate'], fileinfo['technical_replicate']))
                return None
            except AppError, e:
                logger.error("Can not POST this replicate because reasons: %s" % e.message)
                return None
            except Exception, e:
                logger.error("Something untoward (%s) happened trying to create replicates: for %s" % (e, fileinfo))
                sys.exit(1)


    url = collection_url(FILES)
    if not dry_run:
        resp = app.post_json(url, fileinfo, expect_errors=True)
        logger.info(str(resp) + "")
        if resp.status_int == 409:
            logger.warning('Failed POST File %s: File already exists', accession)
        elif resp.status_int < 200 or resp.status_int >= 400:
            logger.error('Failed POST File %s%s', accession, resp)
        else:
            logger.info('Successful POST File: %s' % (accession))
        return resp
    else:
        logger.debug('Sucessful dry-run POST File %s' % (accession))
        return {status_int: 201}


def get_dicts(app, edw, phase=edw_file.ENCODE_PHASE_ALL):

    edw_files = edw_file.get_edw_fileinfo(edw)
    # Other parameters are default
    edw_dict = { d['accession']:d for d in edw_files }
    app_files = get_app_fileinfo(app, phase=phase)
    app_dict = { d['accession']:d for d in app_files }

    return edw_dict, app_dict


def patch_fileinfo(app, props, propinfo, dry_run):
    # PATCH properties to file in app

    accession = propinfo['accession']

    logger.info('....PATCH file: %s' % (accession))
    for prop in props:
        if prop in NO_UPDATE:
            logger.error('Refusing to PATCH %s (%s): for %s' % (prop, propinfo[prop], accession))
            return None

    url = collection_url(FILES) + accession
    if not dry_run:
        resp = app.patch_json(url, propinfo)
        logger.info(str(resp))
        if resp.status_int < 200 or resp.status_int >= 400:
            logger.error('Failed PATCH File %s%s', accession, resp)
            return None
        else:
            logger.info('Successful PATCH File: %s' % (accession))
            return resp
    else:
        logger.debug('Sucessful dry-run PATCH File %s' % (accession))
        return {status_int: 201}


def collection_url(collection):
    # Form URL from collection name
    return '/' + collection + '/'


def get_collection(app, collection):
    # GET JSON objects from app as a list
    # NOTE: perhaps limit=all should be default for JSON output
    # and app should hide @graph (provide an iterator)
    url = collection_url(collection)
    url += "?limit=all"
    resp = app.get(url)
    return resp.json['@graph']


def compare_files(aa, bb):
    a_keys = set(aa.keys())
    b_keys = set(bb.keys())
    intersect_keys = a_keys.intersection(b_keys)
    a_only_keys = a_keys - b_keys
    b_only_keys = b_keys - a_keys

    modified = { o : (aa[o], bb[o]) for o in intersect_keys if aa[o] != bb[o] }
    return modified


def internal_app(configfile, username=''):
    app = get_app(configfile)
    if not username:
        username = IMPORT_USER
    environ = {
        'HTTP_ACCEPT': 'application/json',
        'REMOTE_USER': username,
    }
    return TestApp(app, environ)


def make_app(application, username, password):
    # Configure test app
    logger.info('Using encoded app: %s' % application)


    app = internal_app(application, username)

    # check schema version
    resp = app.get(FILE_PROFILE_URL)
    schema = resp.json['properties']['schema_version']['default']
    if schema != FILE_SCHEMA_VERSION:
        logger.error('ERROR: File schema has changed: is %s, expecting %s' %
                        (schema, FILE_SCHEMA_VERSION))
        sys.exit(1)
    return app


def inventory_files(app, edw_dict, app_dict):
    # Inventory files
    edw_only = []
    app_only = []
    same = []
    diff_accessions = []

    for accession in sorted(edw_dict.keys()):
        edw_fileinfo = edw_dict[accession]
        #edw_exp_fileinfo = set_fileinfo_experiment(app, edw_fileinfo)
        #edw_dict[accession] =  edw_exp_fileinfo  # replaced Encode2 exps with Encode3
        if accession not in app_dict:
            edw_only.append(edw_fileinfo)
        else:
            diff = compare_files(edw_fileinfo, app_dict[accession])
            if diff:
                diff_accessions.append(accession)
                logger.info("File: %s has %s diffs" % (accession, diff))
            else:
                same.append(edw_fileinfo)

    # APP-only files
    for accession in sorted(app_dict.keys()):
        if accession not in edw_dict:
            app_only.append(app_dict[accession])

    return edw_only, app_only, same, diff_accessions


def run(app, app_files, edw_files, phase=edw_file.ENCODE_PHASE_ALL, dry_run=False):


    edw_only, app_only, same, patch = inventory_files(app, edw_files, app_files)
    logger.info("Comparision")
    logger.info("=================")
    logger.info("%s files in EDW only" % len(edw_only))
    logger.info("%s files in encoded only" % len(app_only))
    logger.info("%s files are identical" % len(same))
    logger.info("%s files need to be patched" % len(patch))

    for add in edw_only:
        acc = add['accession']
        url = collection_url(FILES) + acc
        resp = post_fileinfo(app, add, dry_run)

    for update in patch:
        diff = compare_files(app_files[update], edw_files[update])
        patched = patch_fileinfo(app, diff.keys(), edw_files[update], dry_run)



def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Synchronize EDW and encoded files/replicates", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--dry-run', action='store_true', help="Don't post or patch, just report")
    parser.add_argument('-d', '--data_host', default=None,
                        help='data warehouse host (default from my.cnf)')
    parser.add_argument('-a', '--config_uri', default=DEFAULT_INI,
                    help='application url or .ini (default %s)' % DEFAULT_INI)
    parser.add_argument('-u', '--username', default='',
                    help='HTTP username (access_key_id) or import user')
    parser.add_argument('-p', '--password', default='',
                        help='HTTP password (secret_access_key)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose mode')

    parser.add_argument('-P', '--phase',
                            choices=[edw_file.ENCODE_PHASE_2,
                                     edw_file.ENCODE_PHASE_3,
                                     edw_file.ENCODE_PHASE_ALL],
                            default=edw_file.ENCODE_PHASE_ALL,
                    help='restrict EDW files by ENCODE phase accs (default %s)' % edw_file.ENCODE_PHASE_ALL)

    args = parser.parse_args()

    logging.basicConfig()
    logger.setLevel(logging.WARNING)

    if args.verbose:
        logger.setLevel(logging.INFO)


    app = make_app(args.config_uri, args.username, args.password)
    edw = edw_file.make_edw(args.data_host)

    app_files, edw_files = get_dicts(app, edw, phase=args.phase)

    logger.info("Found %s files at encoded; %s files at EDW" % (len(app_files), len(edw_files)))
    return run(app, app_files, edw_files, phase=args.phase, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
