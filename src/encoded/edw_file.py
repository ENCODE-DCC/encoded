################
# File metadata generated at ENCODE Data Warehouse (EDW) and mirrored at encoded

import sys
import datetime
import ConfigParser
from csv import DictReader, DictWriter
from collections import OrderedDict

from sqlalchemy import MetaData, create_engine, select

################
# Globals

ENCODE_PHASE_2 = '2'
ENCODE_PHASE_3 = '3'
ENCODE_PHASE_ALL = 'all'


# NOTE: ordering of fields currently needs to match query order below
FILE_INFO_FIELDS = [
    'accession',
    'date_created',
    'output_type',
    'file_format',
    'dataset',
    'replicate',
    'download_path',
    'submitted_file_name',
    'assembly',
    'md5sum',
    'submitted_by'
]

TECHNICAL_REPLICATE_NUM = 1     # always 1 for now (pending EDW changes)
NA = 'n/a'

# Configuration file
EDW_CONFIG = 'my.cnf'
CHANGE_ME = 'CHANGEME'          # user/pass in .cfg file


################
# Support functions to localize handling of special fields
# e.g. links, datetime

def format_edw_fileinfo(file_dict, exclude=None):
    valid_time = file_dict['date_created']
    file_dict['date_created'] = datetime.datetime.fromtimestamp(
        valid_time).strftime('%Y-%m-%d')
        # TODO: should be isoformat() ?
    for prop in FILE_INFO_FIELDS:
        file_dict[prop] = unicode(file_dict[prop])
    # not type-aware, so we need to force replicate to numeric
        if file_dict['replicate'] == 'pooled' or file_dict['replicate'] == '':
            file_dict['replicate'] = 0
        else:
            #print "File: ", file_dict['accession'], " Replicate: ", file_dict['replicate']
            file_dict['replicate'] = int(file_dict['replicate'])
    if exclude:
        for prop in exclude:
            del file_dict[prop]


################
# Initialization

def make_edw(data_host=None):
    # Connect with EDW database

    # Get configuration from config file
    config = ConfigParser.ConfigParser()
    config.read(EDW_CONFIG)

    site = 'mysql'
    engine = 'mysql'
    if (data_host):
        host = data_host
    else:
        host = config.get(site, 'host')
    db = config.get(site, 'db')
    user = config.get(site, 'user')
    password = config.get(site, 'password')
    if user ==CHANGE_ME or password == CHANGE_ME:
        sys.exit('ERROR: config file "' + EDW_CONFIG + '" needs user and password set')

    # Create db engine
    sys.stderr.write('Connecting to %s://%s/%s...' % (engine, host, db))
    edw_db = create_engine('%s://%s:%s@%s/%s' %
                          (engine, user, password, host, db))
    sys.stderr.write('\n')
    return edw_db


################
# Utility classes and functions

class FileinfoWriter(DictWriter):
    # Write tab-sep file of file info
    def __init__(self, filename=sys.stdout):
        DictWriter.__init__(self, filename, fieldnames=FILE_INFO_FIELDS,
                            delimiter='\t', lineterminator='\n',
                            extrasaction='ignore')

def dump_filelist(fileaccs, header=True, typeField=None):
    # Dump file accessions from list to stdout
    for acc in sorted(fileaccs):
        print acc

def dump_fileinfo(fileinfos, header=True, typeField=None):
    # Dump file info from list of file info dicts to tab-sep file
    # TODO: should be method of FileInfoWriter
    writer = FileinfoWriter()
    if header:
        if typeField is not None:
            sys.stdout.write('%s\t' % 'type')
        writer.writeheader()

    for fileinfo in sorted(fileinfos):
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


def get_edw_fileinfo(edw, limit=None, experiment=True,
                     exclude=None, phase=ENCODE_PHASE_ALL):
    # Read info from file tables at EDW. 
    # Return list of file infos as dictionaries

    # Autoreflect the schema
    meta = MetaData()
    meta.reflect(bind=edw)
    f = meta.tables['edwFile']
    v = meta.tables['edwValidFile']
    u = meta.tables['edwUser']
    s = meta.tables['edwSubmit']

    # Make a connection
    conn = edw.connect()

    # Get info for EDW files
    # List files newest first
    # NOTE: ordering must mirror FILE_INFO_FIELDS
    query = select([v.c.licensePlate.label('accession'),
                    f.c.endUploadTime.label('date_created'),
                    v.c.outputType.label('output_type'),
                    v.c.format.label('file_format'),
                    v.c.experiment.label('dataset'),
                    v.c.replicate.label('replicate'),
                    f.c.edwFileName.label('download_path'),
                    f.c.submitFileName.label('submitted_file_name'),
                    v.c.ucscDb.label('assembly'),
                    f.c.md5.label('md5sum'),
                    u.c.email.label('submitted_by')])
    query = query.where((v.c.fileId == f.c.id) &
              (s.c.id == f.c.submitId) &
              (u.c.id == s.c.userId))
    if experiment:
        query.append_whereclause('edwValidFile.experiment <> ""')
    if phase == '2':
        query.append_whereclause('edwValidFile.experiment like "wgEncode%"')
    elif phase  == '3':
        query.append_whereclause('edwValidFile.experiment like "ENCSR%%"')

    query = query.order_by(f.c.endUploadTime.desc())
    if limit:
        query = query.limit(limit)
    results = conn.execute(query)
    edw_files = []
    for row in results:
        file_dict = dict(row)
        format_edw_fileinfo(file_dict, exclude)
        edw_files.append(file_dict)
    results.close()
    return edw_files
