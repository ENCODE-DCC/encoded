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
ENCODE2_EXP_PROP = 'encode2_dbxrefs' # WARNING: Also in experiment.json
ENCODE2_DS_PROP = 'aliases' ## ucsc_encode_db:wgEncodeXXX
# Schema object names
FILES = 'files'
EXPERIMENTS = 'experiments'
REPLICATES = 'replicates'
DATASETS = 'datasets'
USERS = 'users'

FILE_PROFILE_URL = '/profiles/file.json'

app_host_name = 'localhost'

EPILOG = __doc__

NO_UPDATE = ['md5sum', 'replicate', 'dataset', 'biological_replicate', 'technical_replicate']
IMPORT_USER = 'IMPORT'

logger = logging.getLogger(__name__)

encode2_to_encode3 = {}  # Dict of ENCODE3 accs, keyed by ENCODE 2 acc
encode3_to_encode2 = {}    # Cache experiment ENCODE 2 ref lists

experiments = {}
datasets = {}


class Summary(object):
    ''' holds summary infomation to put output at the end '''
    def __init__(self):
        self.total_encoded_files = 0
        self.total_edw_files = 0
        self.total_encoded_exps = 0
        self.total_encoded_ds = 0
        self.edw_only_files = 0
        self.encoded_only_files = 0
        self.identical_files =0
        self.diff_files = 0
        self.files_posted = 0
        self.files_punted = 0
        self.replicates_posted = 0
        self.files_patched = 0
        self.warning_count = {}
        self.error_count = {}

summary = Summary()

def convert_edw(app, file_dict, phase=edw_file.ENCODE_PHASE_ALL):
    ''' converts EDW file structure to encoded object'''

    logger.info('Found EDW file: %s' % (file_dict['accession']))

    # convert time stamp
    valid_time = file_dict['date_created']
    if (type(valid_time) == float or type(valid_time) == long):
        file_dict['date_created'] = datetime.datetime.fromtimestamp(
           valid_time).strftime('%Y-%m-%d')
    elif not ( ( type(valid_time) == str or type(valid_time) == unicode ) and re.match('\d+-\d+\d+', valid_time) ):
        logger.error("Invalid time string: %s" % valid_time)
        sys.exit(1)


    if (file_dict['lab_error_message'] or file_dict['edw_error_message'] ):
        file_dict['status'] = u'OBSOLETE'
    else:
        file_dict['status'] = u'CURRENT'

    del file_dict['lab_error_message']
    del file_dict['edw_error_message']
     # hide assembly for fastQ's -- (EDW retains it to represent organism)
    if file_dict['file_format'] in ['fasta', 'fastq']:
        del file_dict['assembly']

    resp = app.get('/users/'+file_dict['submitted_by'], status=[200, 301, 404]).maybe_follow()
    if not file_dict['submitted_by'] or resp.status_code != 200:
        msg = "EDW submitter not found"
        summary.error_count[msg] = summary.error_count.get(msg,0) + 1
        logger.error("%s: %s in file %s" % (msg, file_dict['submitted_by'], file_dict['accession']))
    else:
        file_dict['submitted_by'] = resp.json['@id']

    try:
        ds_acc = file_dict['dataset']
    except:
        msg = "File has no dataset or experiment specified in EDW"
        summary.error_count[msg] = summary.error_count.get(msg,0) + 1
        logger.error("%s: %s" % ( msg, file_dict['accession'] ))
        ds_acc = None

    if ds_acc:
        ds = get_dataset_or_experiment(app, ds_acc, phase)
        if not ds:
            msg = "SKIPPING file with dataset that cannot be found (or wrong phase)"
            summary.warning_count[msg] = summary.warning_count.get(msg,0) + 1
            logger.error("%s: %s (%s)" % (msg, file_dict['accession'], ds_acc))
            summary.files_punted = summary.files_punted + 1
            file_dict = { 'accession': ""}
        else:
            file_dict['dataset'] = ds['@id']
            if ds['dataset_type'] == 'experiment':
                file_dict['replicate'] = find_replicate(ds, file_dict)


    try:
        if file_dict.get('biological_replicate', None):
            int(file_dict['biological_replicate'])
    except ValueError:
        msg = "Non-numerical biological replicate:"
        logger.warning("%s: %s; treating as NULL" % (msg, file_dict['biological_replicate']))
        file_dict['biological_replicate'] = None

    if (file_dict.has_key('replicate') and file_dict['replicate']):
        del file_dict['biological_replicate']
        del file_dict['technical_replicate']
            # otherwise we will try tor create the specified one.

    if file_dict.has_key('assembly'):
        ## HACK - these should not be allowed in EDW
        file_dict['assembly'] = re.sub(r'(male\.|female\.|centro\.)', '', file_dict['assembly'])

    if file_dict.has_key('paired_end') and not file_dict['paired_end']:
        del file_dict['paired_end']
        # treat '' as null.

    return file_dict  ## really don't convert None to unicode...
    #return { i : unicode(j) for i,j in file_dict.items() }


def find_replicate(experiment, file_dict):

    ''' special cases if no technical replicate:
    '''

    bio_rep = file_dict['biological_replicate']
    tech_rep = file_dict['technical_replicate']

    if not bio_rep or bio_rep == 'pooled' or bio_rep == 'n/a':
        # expected in some cases
        return None

    matches = []
    if tech_rep:
        matches = [ rep for rep in experiment['replicates']
          if rep['biological_replicate_number'] == int(bio_rep) and
             rep['technical_replicate_number'] == int(tech_rep)]
    else:
        msg = "No tech rep specified (will attempt with tr=1)"
        summary.warning_count[msg] = summary.warning_count.get(msg,0) + 1
        logger.warn("%s: %s (%s)-%s (%s,%s)" % (msg, file_dict['accession'], file_dict['output_type'],
           experiment['accession'], bio_rep, tech_rep))

        matches = [ rep for rep in experiment['replicates']  if rep['biological_replicate_number'] == int(bio_rep) ]
    if len(matches) == 1:
        return matches[0]['@id']
    elif len(matches) > 1:
        msg = "SKIPPING: Matches >1 Replicate"
        summary.error_count[msg] = summary.error_count.get(msg,0) + 1
        logger.error("%s: %s-%s" % (msg, file_dict['accession'], experiment['accession']))
        summary.files_punted = summary.files_punted + 1
        return None
    else:
        msg = "Matches no replicates. Will attempt to create."
        summary.warning_count[msg] = summary.warning_count.get(msg,0) + 1
        logger.warn("%s: %s (%s %s)" % (msg, experiment['accession'], bio_rep, tech_rep))
        return None


def get_dataset_or_experiment(app, accession, phase=edw_file.ENCODE_PHASE_ALL):
    # Map ENCODE2 experiment accession to ENCODE3
    # This will fail if EDW references a dataset instead of expt.

    global datasets
    global experiments
    global encode2_to_encode3
    global encode3_to_encode2

    lookup = encode2_to_encode3.get(accession, [])
    if len(lookup) > 1:
        msg = "Encode2 dataset id maps to multiple ENCSR"
        summary.error_count[msg] = summary.error_count.get(msg,0) + 1
        logger.error("%s: %s %s" % (msg, accession, lookup))
        return None
    elif lookup:
        ec3_acc = lookup.pop()
        logger.info("Encode2 dataset %s maps to %s " % (accession, ec3_acc))
        lookup.add(ec3_acc)
    else:
        ec3_acc = accession

    if (encode3_to_encode2.get(ec3_acc, []) and phase == edw_file.ENCODE_PHASE_3 ):
        logger.info("Dataset %s is not from phase %s" % (ec3_acc, phase))
        return None


    url = '/' + ec3_acc + '/'
    exp_json = experiments.get('/experiments'+url, {})
    if exp_json:
        try:
            if exp_json['replicates'][0]['@id']:
              return exp_json
        except Exception, e:
            logger.info("Need to fetch experiment: %s (%s)" % (ec3_acc, exp_json.get('replicates', "No Replicates")))
    else:
        ds_json = datasets.get('/datasets'+url, {})
        if ds_json:
            return ds_json

    # try to get it even not knowing the type
    try:
        resp = app.get(url).maybe_follow()
    except AppError, e:
        msg = "Dataset/Experiment could not be found in encoded"
        summary.error_count[msg] = summary.error_count.get(msg,0) + 1
        logger.error("%s: %s (%s)" % (msg, ec3_acc, e))
        return None

    if resp.status_code == 200:
        #logger.info("GET: %s (lookup)" % url)
        #logger.info(str(resp))
        if [ t for t in resp.json['@type'] if t == 'experiment' ]:
            experiments[resp.json['@id']] = resp.json
        else:
            datasets[resp.json['@id']] = resp.json
        return resp.json
    else:
        # should never get here!
        return None


def get_missing_filelist_from_lists(app_accs, edw_accs):
    # Find 'new' file accessions: files in EDW having experiment accesion
    #   but missing in app
    new_accs = []
    for accession in edw_accs:
        if accession not in app_accs:
            new_accs.append(accession)
    return new_accs


def get_app_fileinfo(app, phase=edw_file.ENCODE_PHASE_ALL, dataset=''):
    # Get file info from encoded web application
    # Return list of fileinfo dictionaries
    rows = get_collection(app, FILES)
    app_files = []
    for row in sorted(rows, key=itemgetter('accession')):
        url = row['@id']
        resp = app.get(url).maybe_follow()
        #logger.info("GET: %s" % url)
        #logger.info(str(resp))
        fileinfo = resp.json
        # below seems clunky, could search+filter
        if dataset and fileinfo['dataset'] != dataset:
            continue

        elif phase != edw_file.ENCODE_PHASE_ALL:
            file_phase = get_phase(app, fileinfo['dataset'])
            if file_phase != phase:
                    logging.info("File %s is wrong phase (%s)" % (fileinfo['accession'], file_phase))
                    continue
        app_files.append(resp.json)
    return app_files


def get_phase(app, ds_url):

    global encode3_to_encode2

    url2acc = re.compile('\/(experiments|datasets)\/(ENCSR.{6})\/')
    acc = url2acc.match(ds_url).group(2)

    try:
        if encode3_to_encode2[acc]:
            return edw_file.ENCODE_PHASE_2
        return edw_file.ENCODE_PHASE_3
    except:
        pass


def create_replicate(app, dataset, bio_rep_num, tech_rep_num, dry_run=False):

    # create a replicate
    exp = dataset['@id']
    global experiment
    logger.warn("Creating replicate %s %s for %s" % (bio_rep_num, tech_rep_num, exp))
    rep = {
        'experiment': exp,
        'biological_replicate_number': bio_rep_num,
        'technical_replicate_number': tech_rep_num
    }

    logger.info('....POST replicate %d - %d for experiment %s' % (bio_rep_num, tech_rep_num, exp))
    url = collection_url(REPLICATES)
    if not dry_run:
        resp = app.post_json(url, rep, status=[201, 409])

        if resp.status_code == 409:
            # this means that the replicate was created during this run and is probalby NOW valid
            newds = app.get(exp).maybe_follow().json
            matches = [ rep for rep in newds['replicates'] if rep['biological_replicate_number'] == int(bio_rep_num) and
               rep['technical_replicate_number'] == int(tech_rep_num)]

            if len(matches) == 1:
                logger.info("Replicate posting conflicted but found (probably created earlier)")
                experiments[exp] = newds
                return matches[0]['@id']
            else:
                msg = "Replicate posting conflicted, but valid replicate could not be found"
                logger.error("%s: %s (%s, %s)" % (msg, exp, bio_rep_num, tech_rep_num))
                return None

        logger.info(str(resp))
        rep_id = str(resp.json[unicode('@graph')][0]['@id'])
        summary.replicates_posted = summary.replicates_posted + 1
        return rep_id

    else:
        return "/replicate/new"


def post_fileinfo(app, fileinfo, dry_run=False, no_reps=False):
    # POST file info dictionary to open app

    accession = fileinfo['accession']

    logger.info('....POST file: %s' % (accession))
    logger.info("%s" % fileinfo)

    if fileinfo.get('dataset', None):
        fileinfo = try_replicate(app, fileinfo, dry_run, no_reps=no_reps)
        if not fileinfo:
            return None

    url = collection_url(FILES)
    if not dry_run:
        resp = app.post_json(url, fileinfo, expect_errors=True)  #?collection_sourcd=db
        logger.info(str(resp) + "")
        if resp.status_int == 409:
            msg = "Failed to POST file (File already exists)"
            summary.error_count[msg] = summary.error_count.get(msg,0) + 1
            logger.error("%s: %s", (msg, accession))
        elif resp.status_int < 200 or resp.status_int >= 400:
            msg = "POST file failed"
            summary.error_count[msg] = summary.error_count.get(msg,0) + 1
            logger.error("%s: %s %s" % (msg, accession, resp))
        else:
            summary.files_posted = summary.files_posted + 1
            logger.info('Successful POST File: %s' % (accession))
        return resp
    else:
        logger.warning('Sucessful dry-run POST File %s' % (accession))
        return {'status_int': 201}

def try_replicate(app, fileinfo, dry_run, method='POST', no_reps=False):

    global experiments
    global datasets

    ds = fileinfo['dataset']
    dataset = None
    is_experiment = True
    dataset = experiments.get(ds, None)
    if not dataset:
        dataset = datasets.get(ds, None)
        is_experiment = False
    rep = fileinfo.get('replicate', None)

    if ( (dataset and not is_experiment) or
       ( not rep and not fileinfo['biological_replicate'] and not fileinfo['technical_replicate'] and
         (fileinfo['file_format'] != 'fastq' or fileinfo['file_format'] != 'bam')) ):
        # dataset primary files have irrelvant replicate info
        # non fastq non bam files can have no replicate specified
        del fileinfo['biological_replicate']
        del fileinfo['technical_replicate']
        fileinfo.pop('replicate', None)
    elif not rep and not no_reps:
        try:
            br = int(fileinfo['biological_replicate'])
            tr = int(fileinfo['technical_replicate'])
            fileinfo['replicate'] = create_replicate(app, dataset, br, tr, dry_run)
            del fileinfo['biological_replicate']
            del fileinfo['technical_replicate']
            return fileinfo
        except ValueError, e:
            msg = "Refusing to %s file with confusing replicate ids" % method
            summary.error_count[msg] = summary.error_count.get(msg,0) + 1
            logger.error("%s: %s (%s, %s)" % (msg, fileinfo['accession'], fileinfo['biological_replicate'], fileinfo['technical_replicate']))
            logger.info("%s" % e.message)
            return None
        except KeyError, e:
            msg = "Refusing to %s file with missing replicate ids" % method
            summary.error_count[msg] = summary.error_count.get(msg,0) + 1
            logger.error("%s: %s (%s, %s)" % (msg, fileinfo['accession'], fileinfo['biological_replicate'], fileinfo['technical_replicate']))
            logger.info("%s" % e.message)
            return None
        except AppError, e:
            msg = "Could not %s replicate" % method
            summary.error_count[msg] = summary.error_count.get(msg,0) + 1
            logger.error("%s: %s (%s, %s)" % (msg, fileinfo['accession'], fileinfo['biological_replicate'], fileinfo['technical_replicate']))
            logger.info("%s" % e.message)
            return None
        except Exception, e:
            logger.error("Something untoward (%s) happened trying to create replicates: for %s" % (e, fileinfo))
            sys.exit(1)

    return fileinfo

def get_dicts(app, edw, phase=edw_file.ENCODE_PHASE_ALL, enc_dataset='', edw_dataset='', since=0, test=False):

    edw_files = edw_file.get_edw_fileinfo(edw, phase=phase, dataset=edw_dataset, since=since, test=test)
    # Other parameters are default
    edw_dict = { d['accession']:convert_edw(app, d, phase) for d in edw_files }
    app_files = get_app_fileinfo(app, phase=phase, dataset=enc_dataset)
    app_dict = { d['accession']:d for d in app_files }

    return edw_dict, app_dict

def try_datasets(app, phase=edw_file.ENCODE_PHASE_ALL, dataset=''):

    global experiments
    global datasets
    if dataset:
        try:
            eurl = collection_url(EXPERIMENTS) + dataset + '/'
            exp = app.get(eurl).maybe_follow().json
            experiments[exp['@id']] = exp
            #logger.info("GET: %s" % eurl)
            logger.info(str(exp))
            return exp['@id']
        except:
            durl = collection_url(DATASETS) + dataset + '/'
            ds = app.get(durl).maybe_follow.json
            datasets[ds['@id']] = ds
            #logger.info("GET: %s" % durl)
            logger.info(str(ds))
            return ds['@id']

        logger.error("Dataset %s requested but not found" % dataset)
        sys.exit(1)
    else:
        return get_all_datasets(app, phase=phase)

def get_all_datasets(app, phase=edw_file.ENCODE_PHASE_ALL):

    global experiments
    global datasets

    logger.info("Getting all experiments...")
    exp_collection = get_collection(app, EXPERIMENTS)
    logger.warn("Found %s experiments" % len(exp_collection))

    for exp in exp_collection:
        dbxrefs = exp[ENCODE2_EXP_PROP]
        acc = exp['accession']
        for xref in dbxrefs:
            e2e3 = encode2_to_encode3.get(xref, set())
            e2e3.add(acc)
            encode2_to_encode3[xref] = e2e3

        e3e2 = encode3_to_encode2.get(acc,set())
        e3e2.update(set(dbxrefs))
        encode3_to_encode2[acc] = e3e2

        experiments[exp['@id']] = exp


    logger.info("Getting all datasets...")
    alias_key = 'ucsc_encode_db:'
    ds_collection = get_collection(app, DATASETS)
    logger.warn("Found %s datasets" % len(ds_collection))

    for ds in ds_collection:
        acc = ds['accession']
        aliases = ds[ENCODE2_DS_PROP]
        for al in aliases:
            if al.startswith(alias_key):
                dbxref = al.replace(alias_key, '')

                e2e3 = encode2_to_encode3.get(dbxref, set())
                e2e3.add(acc)
                encode2_to_encode3[dbxref] = e2e3

                e3e2 = encode3_to_encode2.get(acc,set())
                e3e2.add(dbxref)
                encode3_to_encode2[acc] = e3e2

        datasets[ds['@id']] = ds
        ## don't need replicates or anything.
    logger.warn("%s Encode2 experiments can be referenced" % len(encode2_to_encode3.keys()))
    return '';

def patch_fileinfo(app, props, propinfo, dry_run=False, no_reps=False):
    # PATCH properties to file in app

    #TODO: handle this case in test:
    #webtest.app.AppError: Bad response: 422 Unprocessable Entity (not one of 200, 201, 409 for http://localhost/files/ENCFF001MXD)
    #{"status": "error", "errors": [{"location": "body", "name": ["replicate"], "description": "None is not of type u'string'"}, {"location": "body", "name": [], "description": "Additional properties are not allowed (u'technical_replicate', u'biological_replicate' were unexpected)"}], "description": "Failed validation", "title": "Unprocessable Entity", "code": 422, "@type": ["ValidationFailure", "error"]}
    accession = propinfo['accession']

    logger.info('....PATCH file: %s' % (accession))
    can_patch_replicates = False
    for prop in props:
        if prop in NO_UPDATE:
            msg = "Refusing to PATCH %s" % prop
            summary.error_count[msg] = summary.error_count.get(msg,0) + 1
            logger.error("%s: (%s) for %s" % (msg, propinfo[prop], accession))
            return None
        elif prop == 'replicate':
            can_patch_replicates = True

    if not propinfo['replicate']:
        propinfo = try_replicate(app, propinfo, dry_run, method='PATCH', no_reps=no_reps)

    url = collection_url(FILES) + accession
    if not dry_run:
        resp = app.patch_json(url, propinfo, status=[200, 201, 409, 422])
        logger.info(str(resp))
        if resp.status_int < 200 or resp.status_int == 409 or resp.status_int == 422:
            msg = "PATCH failed for"
            summary.error_count[msg] = summary.error_count.get(msg,0) + 1
            logger.error("%s: %s (%s)" % (msg, accession, resp))
            return None
        else:
            logger.info('Successful PATCH File: %s' % (accession))
            summary.files_patched = summary.files_patched + 1
            return resp
    else:
        logger.debug('Sucessful dry-run PATCH File %s' % (accession))
        return {'status_int': 201}


def collection_url(collection):
    # Form URL from collection name
    return '/' + collection + '/'


def get_collection(app, collection):
    # GET JSON objects from app as a list
    # NOTE: perhaps limit=all should be default for JSON output
    # and app should hide @graph (provide an iterator)
    # frame=object is the default
    url = collection_url(collection)
    url += "?limit=all&datastore=database&frame=object"
    resp = app.get(url)
    return resp.json['@graph']


def compare_files(aa, bb):
    ##  aa is usually encoded
    ## bb is usually edw
    a_keys = set(aa.keys())
    b_keys = set(bb.keys())
    intersect_keys = a_keys.intersection(b_keys)
    a_only_keys = a_keys - b_keys
    b_only_keys = b_keys - a_keys

    modified = { o : (aa[o], bb[o]) for o in intersect_keys if aa[o] != bb[o] }
    if b_only_keys:
        logger.info("EDW file has additional fields: %s" % b_only_keys)
        for new_key in b_only_keys:
            if new_key not in NO_UPDATE:
                modified[new_key] = (bb[new_key], None)

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


def make_app(application, username, password, test=False):
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
        if not edw_fileinfo['accession']:
            continue
            # most likely dropped out due to wrong phase
        if accession not in app_dict:
            edw_only.append(edw_fileinfo)
        else:
            diff = compare_files(app_dict[accession], edw_fileinfo)
            if diff:
                diff_accessions.append(accession)
                logger.warn("File: %s has %s DIFFS (encoded, EDW) - PATCH if valid" % (accession, diff))
            else:
                same.append(edw_fileinfo)

    # APP-only files
    for accession in sorted(app_dict.keys()):
        if accession not in edw_dict:
            app_only.append(app_dict[accession])

    return edw_only, app_only, same, diff_accessions


def run(app, app_files, edw_files, phase=edw_file.ENCODE_PHASE_ALL, dry_run=False, no_patch=False, no_reps=False):


    edw_only, app_only, same, patch = inventory_files(app, edw_files, app_files)

    summary.edw_only_files = len(edw_only)
    summary.app_only_files = len(app_only)
    summary.identical_files = len(same)
    summary.diff_files = len(patch)

    logger.warn("SUMMARY: %s files in EDW only" % summary.edw_only_files)
    logger.warn("SUMMARY: %s files in encoded only" % summary.app_only_files)
    logger.warn("SUMMARY: %s files are identical" % summary.identical_files)
    logger.warn("SUMMARY: %s files need to be patched" % summary.diff_files)

    for add in edw_only:
        acc = add['accession']
        url = collection_url(FILES) + acc
        resp = post_fileinfo(app, add, dry_run=dry_run, no_reps=no_reps)

    logger.warn("SUMMARY: %s files sucessfully posted" % summary.files_posted)

    if not no_patch:
        for update in patch:
            diff = compare_files(app_files[update], edw_files[update])
            patched = patch_fileinfo(app, diff.keys(), edw_files[update], dry_run=dry_run, no_reps=no_reps)
        logger.warn("SUMMARY: %s files succesfully patched" % summary.files_patched)

    logger.warn("SUMMARY: %s replicates sucessfully posted" % summary.replicates_posted)
    logger.warn("SUMMARY: %s files were given up on" % summary.files_punted)

    total_errors = 0
    for err in summary.error_count.keys():
        logger.warn("SUMMARY: %s errors of type: %s" % (summary.error_count[err], err))
        total_errors = summary.error_count[err] + total_errors

    total_warnings = 0
    for warn in summary.warning_count.keys():
        logger.warn("SUMMARY: %s warnings of type: %s" % (summary.warning_count[warn], warn))
        total_warnings = summary.warning_count[warn] + total_warnings

    logger.warn("SUMMARY: %s total errors, %s total warnings" % (total_errors, total_warnings))

def main():
    global NO_UPDATE
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

    parser.add_argument('--patch-replicates', action='store_true',
               help='NEVER USE THIS.  But if you do, you must use with single dataset option -E')

    parser.add_argument('-E', '--experiment', default='',
               help="Only sync files from a single ENCSR dataset/experiment.")

    parser.add_argument('-S', '--time-since', type=int, default=0,
               help="Only sync files from EDW in the last <int> hours")

    parser.add_argument('-n', '--no-patch', action='store_true',
               help="Only POST new files do not patch")

    parser.add_argument('-T', '--use-test', action='store_true',
               help="Do not filter files in EDW that begin with TST instead of ENCFF")

    parser.add_argument('--no-replicates', action='store_true',
               help="Do not create replicates at all", default=False)

    zargs = parser.parse_args()

    FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.WARNING)

    if zargs.verbose:
        logger.setLevel(logging.INFO)

    since = 0
    if zargs.time_since:
        from datetime import datetime;
        from datetime import timedelta
        today = datetime.today()
        since_dt = today - timedelta(hours=zargs.time_since)
        since = int(since_dt.strftime("%s"))
        logger.info("Today is %s" % today)
        logger.warning("Getting files uploaded to EDW since %s (%s)" % (since_dt, since))

    if zargs.dry_run:
        logger.warning("DRY-RUN: will not POST or PATCH database")

    if zargs.patch_replicates:
        logger.warning("WILL attempt to PATCH replicates!  Careful!")
        update = [ x for x in NO_UPDATE if x != 'replicate' ]
        NO_UPDATE = update

    if zargs.experiment and zargs.phase != edw_file.ENCODE_PHASE_ALL:
        logger.error("Phase (-P) and single dataset (-E/--experiment) not compatible options")
        sys.exit(1)

    if zargs.experiment:
        logger.warning("Only fetching from Dataset: %s" % zargs.experiment)

    if zargs.no_patch:
        logger.warning("Will not PATCH files, only POST")

    if zargs.use_test:
        logger.warning("Will fetch TST accessions from EDW")
        zargs.config_uri = 'test_accession.ini'

    if (zargs.patch_replicates and not zargs.experiment):
        logger.error("Not allowed to patch replicates for all; please use -E (--experiment) to select a dataset.")
        sys.exit(1)

    if (zargs.no_replicates):
        logger.warning("Will not POST new replicates by user request")

    if (zargs.no_patch):
        logger.warning("Will not do any PATCHing by user request")

    app = make_app(zargs.config_uri, zargs.username, zargs.password, test=zargs.use_test)
    edw = edw_file.make_edw(zargs.data_host)

    try:
        edw.connect()
    except Exception, e:
        logger.error("Could not connect to: %s; aborting" % zargs.data_host)
        logger.error("%s", e)
        sys.exit(1)

    single = try_datasets(app, dataset=zargs.experiment)
    summary.total_encoded_exps = len(experiments.keys())
    summary.total_encoded_ds = len(datasets.keys())

    edw_files, app_files = get_dicts(app, edw, phase=zargs.phase, edw_dataset=zargs.experiment, enc_dataset=single, since=since, test=zargs.use_test)

    summary.total_encoded_files = len(app_files)
    summary.total_edw_files = len(edw_files)
    logger.warn("SUMMARY: Found %s files at encoded; %s files at EDW" % (summary.total_encoded_files, summary.total_edw_files))
    if zargs.phase != edw_file.ENCODE_PHASE_ALL:
        logger.warn("SUMMARY: Synching files from Phase %s only" % zargs.phase)

    return run(app, app_files, edw_files, phase=zargs.phase, dry_run=zargs.dry_run, no_patch=zargs.no_patch, no_reps=zargs.no_replicates)


if __name__ == '__main__':
    main()
