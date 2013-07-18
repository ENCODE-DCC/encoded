from PIL import Image
from base64 import b64encode
from typedsheets import cast_rows, remove_nulls
import datetime
import logging
import mimetypes
import os.path
import xlrd
import xlreader
from zipfile import ZipFile
# http://www.lexicon.net/sjmachin/xlrd.html

logger = logging.getLogger('encoded')
logger.setLevel(logging.INFO)  # doesn't work to shut off sqla INFO

TYPE_URL = {
    # TODO This has appears in 3 places... maybe it shoudl be configged
    'organism': '/organisms/',
    'source': '/sources/',
    'target': '/targets/',
    'antibody_lot': '/antibody-lots/',
    'antibody_validation': '/validations/',
    'antibody_approval': '/antibodies/',
    'donor': '/donors/',
    'document': '/documents/',
    'biosample': '/biosamples/',
    'treatment': '/treatments/',
    'construct': '/constructs/',
    'colleague': '/users/',
    'lab': '/labs/',
    'award': '/awards/',
    'platform': '/platforms/',
    'library': '/libraries/',
    'assay': '/assays/',  # this should be removed lated
    'replicate': '/replicates/',
    'file': '/files/',
    'experiment': '/experiments/',
}

ORDER = [
    'organism',
    'source',
    'lab',
    'colleague',
    'award',
    'target',
    'antibody_lot',
    'antibody_validation',
    'antibody_approval',
    'donor',
    'document',
    'treatment',
    'construct',
    'biosample',
    'platform',
    'library',
    'assay',
    'replicate',
    'file',
    'experiment',
]


def find_doc(docsdir, filename):
    path = None
    for dirpath in docsdir:
        candidate = os.path.join(dirpath, filename)
        if not os.path.exists(candidate):
            continue
        if path is not None:
            msg = 'Duplicate filenames: %s, %s' % (path, candidate)
            raise AssertionError(msg)
        path = candidate
    if path is None:
        raise ValueError('File not found: %s' % filename)
    return path


def trim(value):
    """ Shorten over long binary fields in error log
    """
    trimmed = {}
    for k, v in value.iteritems():
        if isinstance(v, dict):
            trimmed[k] = trim(v)
        elif isinstance(v, basestring) and len(v) > 100:
            trimmed[k] = v[:40] + '...'
        else:
            trimmed[k] = v
    return trimmed



def read_single_sheet(filename, name):
    assert filename.endswith('.zip')
    zf = ZipFile(filename)
    filename = name + '.xlsx'
    f = zf.open(filename)
    book = xlrd.open_workbook(file_contents=f.read())
    sheet, = book.sheets()
    return xlreader.DictReader(sheet)


def filter_test_only(dictrows, filter_test_only=False, **settings):
    for row in dictrows:
        test = row.pop('test', True)
        if filter_test_only and not test:
            continue
        yield row


def filter_missing_key(dictrows, key):
    for row in dictrows:
        if not row[key]:
            continue
        yield row

def filter_key(dictrows, key):
    for row in dictrows:
        if key in row:
            row = row.copy()
            del row[key]
        yield row


def image_data(stream, filename=None):
    data = {}
    if filename is not None:
        data['download'] = filename
    im = Image.open(stream)
    im.verify()
    data['width'], data['height'] = im.size
    mime_type, _ = mimetypes.guess_type('name.%s' % im.format)
    data['type'] = mime_type
    data['href'] = data_uri(stream, mime_type)
    return data


def data_uri(stream, mime_type):
    stream.seek(0, 0)
    encoded_data = b64encode(stream.read())
    return 'data:%s;base64,%s' % (mime_type, encoded_data)



def update(testapp, url, value):
    res = testapp.post_json(url, value, status='*')
    if res.status == 200:
        logger.debug('%s UPDATED' % url)
    elif res.status_int == 404:
        logger.debug('%s not found for UPDATE, posting as new' % url)
    elif res.status_int == 422:
        logger.warn('Error VALIDATING for UPDATE %s: %r. Value:\n%r\n' % (url, res.json['errors'], trim(value)))
    else:
        logger.warn('Error UPDATING %s: %s. Value:\n%r\n' % (url, res.status, trim(value)))
    return res


def create(testapp, url, value):
    uuid = value['uuid']
    res = testapp.post_json(url, value, status='*')
    if res.status_int == 201:
        pass
    elif res.status_int == 422:
        logger.warn('Error VALIDATING NEW %s %s: %r. Value:\n%r\n' % (url, uuid, res.json['errors'], trim(value)))
    else:
        logger.warn('Error SUBMITTING NEW %s %s: %s. Value:\n%r\n' % (url, uuid, res.status, trim(value)))
    return res


def post_collection(testapp, url, rows):
    count = 0
    nload = 0
    nupdate = 0
    for row in rows:
        count += 1
        uuid = row['uuid']
        update_url = url+row['uuid']+'/'
        res = update(testapp, update_url, row)
        if res.status_int == 200:
            nupdate += 1
        if res.status_int != 404:
            continue
        res = create(testapp, url, row)
        if res.status_int == 201:
            nload += 1
    nerrors = count - nload - nupdate
    logger.info('Loaded %d for %s. NEW: %d, UPDATE: %d, ERRORS: %d' % (count, url, nload, nupdate, nerrors))


def check_document(docsdir, filename):

    _, ext = os.path.splitext(filename.lower())

    doc = {}
    if ext:
        stream = open(find_doc(docsdir, filename), 'rb')
        if ext in ('.png', '.jpg', '.jpeg', '.tiff', '.tif', '.gif'):
            doc = image_data(stream, filename)

        elif ext == '.pdf':
            mime_type = 'application/pdf'
            doc = {
                'download': filename,
                'type': mime_type,
                'href': data_uri(stream, mime_type)
            }
        elif ext == '.txt':
            mime_type = 'text/plain'
            doc = {
                'download': filename,
                'type': mime_type,
                'href': data_uri(stream, mime_type)
            }

        else:
            raise ValueError("Unknown file type for %s" % filename)

    return doc


def add_document(dictrows, docsdir=(), **settings):
    for row in dictrows:
        filename = row['document']
        row['document'] = check_document(docsdir, filename)
        yield row



def default_pipeline(reader, **settings):
    pipeline = cast_rows(reader)
    pipeline = remove_nulls(pipeline)
    pipeline = filter_test_only(pipeline, **settings)
    pipeline = filter_missing_key(pipeline, key='uuid')
    pipeline = filter_key(pipeline, key='schema_version')
    return pipeline


def document_pipeline(pipeline, **settings):
    pipeline = add_document(pipeline, **settings)
    return pipeline




PIPELINE = {
    'antibody_validation': document_pipeline,
}

import pdb, sys, traceback

def load_all(testapp, filename, docsdir, test=False):
    for item_type in ORDER:
        try:
            url = TYPE_URL[item_type]
            reader = read_single_sheet(filename, item_type)
            pipeline = default_pipeline(reader, docsdir=docsdir, filter_test_only=test)
            extra = PIPELINE.get(item_type)
            if extra is not None:
                pipeline = extra(pipeline, docsdir=docsdir, filter_test_only=test)
            post_collection(testapp, url, pipeline)
        except:
            type, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)