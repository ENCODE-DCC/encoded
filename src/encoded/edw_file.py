###############
# File metadata generated at ENCODE Data Warehouse (EDW) and mirrored at encoded

import sys
import datetime
import ConfigParser
from csv import DictReader, DictWriter
from collections import OrderedDict
from operator import itemgetter

from sqlalchemy import MetaData, create_engine, select
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

################
# Globals

# ENCODE project -- phase 2 at UCSC, accessions like 'wgEncodeE*',
#   ENCODE 3 at Stanford, accessions like 'ENCSR*'

ENCODE_PHASE_2 = '2'
ENCODE_PHASE_3 = '3'
ENCODE_PHASE_ALL = 'all'


# Column headers for file info TSV
# NOTE: ordering of fields currently needs to match query order below
FILE_INFO_FIELDS = [
    'accession',
    'date_created',
    'output_type',
    'file_format',
    'dataset',
    'biological_replicate',
    'technical_replicate',
    'download_path',
    'submitted_file_name',
    'assembly',
    'md5sum',
    'submitted_by',
    'status',
]

# Replicate representation
#TECHNICAL_REPLICATE_NUM = 1  # always 1 for now (pending EDW changes)
NO_REPLICATE_TERMS = ['pooled', 'n/a', '']  # in manifest files and EDW tables
NO_REPLICATE_INT = -1   # integer used in TSV replicate column

NA = 'n/a'

# Configuration file
EDW_CONFIG = 'my.cnf'
CHANGE_ME = 'CHANGEME'          # user/pass in .cfg file

verbose = False

################
# Support functions to localize handling of special fields

def format_edw_fileinfo(file_dict, exclude=None):
    ''' depecated here, conversion functionality moved to read_edw_fileinfo'''
    global verbose
    if verbose:
        sys.stderr.write('Found EDW file: %s\n' % (file_dict['accession']))
    valid_time = file_dict['date_created']
    file_dict['date_created'] = datetime.datetime.fromtimestamp(
        valid_time).strftime('%Y-%m-%d')
        # TODO: should be isoformat() ?
    ''' from previous method
    file_dict = dict(row)
    file_dict['status'] = file_dict['lab_error_message'] + file_dict['edw_error_message']
    del file_dict['lab_error_message']
    del file_dict['edw_error_message']
    format_edw_fileinfo(file_dict, exclude)
    edw_files.append(file_dict)
    '''

    if file_dict['status'] == '':
        file_dict['status'] = 'CURRENT'
    else:
        file_dict['status'] = 'OBSOLETE'
    for prop in FILE_INFO_FIELDS:
        file_dict[prop] = unicode(file_dict[prop])
        # not type-aware, so we need to force replicate to numeric
        '''if not file_dict.get('biological_replicate'):
            pass
        elif file_dict['biological_replicate'] in NO_REPLICATE_TERMS:
            #file_dict['replicate'] = NO_REPLICATE_INT
            del file_dict['biological_replicate']
        else:
            file_dict['biological_replicate'] = int(file_dict['biological_replicate'])
        '''
    # hide assembly for fastQ's -- (EDW retains it to represent organism)
    if file_dict['file_format'] in ['fasta', 'fastq']:
        del file_dict['assembly']
    if exclude:
        for prop in exclude:
            if prop in file_dict:
                del file_dict[prop]


################
# Initialization

def make_edw(data_host=None):
    # Connect with EDW database

    # Get configuration from config file
    config = ConfigParser.ConfigParser()
    config.read(EDW_CONFIG)

    engine = 'mysql'
    site = 'mysql'
    # TODO: Change to more informative identifier (also need to change my.cnf*)
    # site = 'edw'
    if (data_host):
        host = data_host
    else:
        host = config.get(site, 'host')
    db = config.get(site, 'database')
    user = config.get(site, 'user')
    password = config.get(site, 'password')
    if user ==CHANGE_ME or password == CHANGE_ME:
        sys.exit('ERROR: config file "' + EDW_CONFIG + '" needs user and password set')

    # Create db engine
    sys.stderr.write('Connecting to %s://%s/%s...' % (engine, host, db))
    cnx_str = '%s://%s:%s@%s/%s' % (engine, user, password, host, db)
    edw_db = create_engine(cnx_str)

    # TODO: A nice-to-have suggested by Laurence -- have MySQL directly read conf file.
    # Something like the commented-out code below should do the trick.
    # Could be a path problem preventing mysql from finding the proper user
    # (is using invoker, not user in .cnf file)

    # Create db engine
    # from sqlalchemy.engine.url import URL
    # url = URL(drivername=engine, host=host, query={'read_default_file': EDW_CONFIG, 'read_default_group': site})
    # edw_db = create_engine(name_or_url=url)

    sys.stderr.write('\n')
    return edw_db


################
# Utility classes and functions

class FileinfoWriter(DictWriter):
    # Write tab-sep file of file info
    def __init__(self, filename=sys.stdout, exclude=None):
        if exclude:
            fields = list(set(FILE_INFO_FIELDS) ^ set(exclude))
        else:
            fields = FILE_INFO_FIELDS
        DictWriter.__init__(self, filename, fieldnames=fields,
                            delimiter='\t', lineterminator='\n',
                            extrasaction='ignore')

def dump_filelist(fileaccs, header=True, typeField=None):
    # Dump file accessions from list to stdout
    for acc in sorted(fileaccs):
        print acc

def dump_fileinfo(fileinfos, header=True, typeField=None, exclude=None):
    # Dump file info from list of file info dicts to tab-sep file
    # TODO: should be method of FileInfoWriter
    writer = FileinfoWriter(exclude=exclude)
    if header:
        if typeField is not None:
            sys.stdout.write('%s\t' % 'type')
        writer.writeheader()

    for fileinfo in sorted(fileinfos, key=itemgetter('accession')):
        if typeField is not None:
            sys.stdout.write('%s\t' % typeField)
        ordered = OrderedDict.fromkeys(FILE_INFO_FIELDS)
        for key in FILE_INFO_FIELDS:
            if key in fileinfo:
                ordered[key] = fileinfo[key]
            else:
                ordered[key] = NA
        writer.writerow(ordered)


def get_edw_filelist(edw, limit=None, experiment=True, phase=ENCODE_PHASE_ALL):
    # Read info from file tables at EDW.
    # Return list of file infos as dictionaries

    # Autoreflect the schema
    meta = MetaData()
    meta.reflect(bind=edw)
    v = meta.tables['edwValidFile']

    # Make a connection
    conn = edw.connect()

    # Get info for EDW files
    # List files newest first
    # NOTE: ordering must mirror FILE_INFO_FIELDS
    query = select([v.c.licensePlate.label('accession')])

    if experiment:
        query.append_whereclause('edwValidFile.experiment <> ""')
    if phase == '2':
        query.append_whereclause('edwValidFile.experiment like "wgEncode%"')
    elif phase  == '3':
        query.append_whereclause('edwValidFile.experiment like "ENCSR%%"')
    if limit:
        query = query.limit(limit)
    results = conn.execute(query)
    edw_accs = []
    for row in results:
        file_dict = dict(row)
        edw_accs.append(file_dict['accession'])
    results.close()
    return edw_accs


def get_edw_max_id(edw):
    # Get current largest id from edwValidFile table at EDW
    conn = edw.connect()
    query = 'select max(id) from edwValidFile'
    results = conn.execute(query)
    row = results.fetchone()
    max_id = int(row[0])
    results.close()
    if verbose:
        sys.stderr.write('EDW max id: %d\n' % (int(max_id)))
    return max_id


def get_edw_fileinfo(edw, limit=None, experiment=True, start_id=0,
                     phase=ENCODE_PHASE_ALL):
    # Read info from file tables at EDW
    # Optional param max_id limits to just files having EDW id greater
    # than the named value (typically, this was from previous sync)
    # Return list of file infos as dictionaries

    # Autoreflect the schema
    meta = MetaData()
    meta.reflect(bind=edw)

    try:
        f = meta.tables['edwFile']
        v = meta.tables['edwValidFile']
        u = meta.tables['edwUser']
        s = meta.tables['edwSubmit']
    except (DBAPIError, SQLAlchemyError) as e:
        sys.stderr.write("ERROR: EDW schema binding failed (suspect schema change)\n")
        exit(-1)

    # Make a connection
    conn = edw.connect()

    # Get info for EDW files
    # List files newest first
    # NOTE: ordering must mirror FILE_INFO_FIELDS
    try:
        query = select([v.c.licensePlate.label('accession'),
                    f.c.endUploadTime.label('date_created'),
                    v.c.outputType.label('output_type'),
                    v.c.format.label('file_format'),
                    v.c.experiment.label('dataset'),
                    v.c.replicate.label('biological_replicate'),
                    v.c.technicalReplicate.label('technical_replicate'),
                    f.c.edwFileName.label('download_path'),
                    f.c.submitFileName.label('submitted_file_name'),
                    v.c.ucscDb.label('assembly'),
                    f.c.md5.label('md5sum'),
                    u.c.email.label('submitted_by'),
                    v.c.pairedEnd.label('paired_end'),
                    # either of these two error fields will cause status to be OBSOLETE
                    f.c.deprecated.label('lab_error_message'),
                    f.c.errorMessage.label('edw_error_message')])
        query = query.where(
              (v.c.fileId == f.c.id) &
              (u.c.id == s.c.userId) &
              (s.c.id == f.c.submitId) &
              (u.c.id == s.c.userId))
        if start_id > 0:
            query.append_whereclause('edwValidFile.id > ' + str(start_id))
        if experiment:
            query.append_whereclause('(edwValidFile.experiment like "wgEncodeE%" or edwValidFile.experiment like "ENCSR%")')
        if phase == '2':
            query.append_whereclause('edwValidFile.experiment like "wgEncodeE%"')
        elif phase  == '3':
            query.append_whereclause('edwValidFile.experiment like "ENCSR%"')
        query.append_whereclause('edwValidFile.licensePlate like "ENCFF%"')  ## skip TST

        query = query.order_by(f.c.endUploadTime.desc())
        if limit:
            query = query.limit(limit)
        results = conn.execute(query)
    except (DBAPIError, SQLAlchemyError) as e:
        sys.stderr.write("ERROR: EDW SQL query failed (suspect schema change)\n")
        exit(-1)

    files =  [ dict(row) for row in results ]
    results.close()
    conn.close()
    return files
