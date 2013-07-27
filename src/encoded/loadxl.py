from typedsheets import cast_row_values
import logging
import os.path

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
    'mouse_donor': '/mouse-donors/',
    'human_donor': '/human-donors/',
    'document': '/documents/',
    'biosample': '/biosamples/',
    'treatment': '/treatments/',
    'construct': '/constructs/',
    'construct_validation': '/construct-validations/',
    'colleague': '/users/',
    'lab': '/labs/',
    'award': '/awards/',
    'platform': '/platforms/',
    'library': '/libraries/',
    'replicate': '/replicates/',
    'software': '/software/',
    'file': '/files/',
    'dataset': '/datasets/',
    'experiment': '/experiments/',
    'rnai': '/rnai/',
}

ORDER = [
    'colleague',
    'award',
    'lab',
    'organism',
    'source',
    'target',
    'antibody_lot',
    'antibody_validation',
    'antibody_approval',
    'mouse_donor',
    'human_donor',
    'document',
    'treatment',
    'construct',
    'construct_validation',
    'rnai',
    'biosample',
    'platform',
    'library',
    'experiment',
    'replicate',
    # 'software',
    'file',
    # 'dataset',
]


##############################################################################
# Pipeline components
#
# http://www.stylight.com/Numbers/pipes-and-filters-architectures-with-python-generators/
#
# Dictionaries are passed through the pipeline. By convention, values starting
# with an underscore (_) are ignored by the component posting a final value
# so are free for communicating information down the pipeline.


def noop(dictrows):
    """ No-op component

    Useful for pipeline component factories.
    """
    return dictrows


def skip_test_column_value_skip(dictrows):
    for row in dictrows:
        if row.get('test', '') == 'skip':
            row['_skip'] = True
        yield row


def remove_keys_with_empty_value(dictrows):
    for row in dictrows:
        yield {
            k: v for k, v in row.iteritems()
            if k and v not in ('', None, [])
        }


##############################################################################
# Pipeline component factories


def remove_keys_with_unknown_value_except_for(*keys):
    def component(dictrows):
        for row in dictrows:
            yield {
                k: v for k, v in row.iteritems()
                if k in keys or unicode(v).lower() != 'unknown'
            }

    return component


def skip_rows_missing_all_keys(*keys):
    def component(dictrows):
        for row in dictrows:
            if not any(key in row for key in keys):
                row['_skip'] = True
            yield row

    return component


def remove_keys(*keys):
    def component(dictrows):
        for row in dictrows:
            for key in keys:
                row.pop(key, None)
            yield row

    return component


def filter_test_only(test_only):
    if not test_only:
        return noop

    def component(dictrows):
        for row in dictrows:
            if row.get('test', True):
                yield row

    return component


def add_attachment(docsdir):
    def component(dictrows):
        for row in dictrows:
            filename = row.get('attachment', None)
            if filename is None:
                yield row
                continue
            try:
                path = find_doc(docsdir, filename)
                row['attachment'] = attachment(path)
            except ValueError, e:
                row['_errors'] = repr(e)
            yield row

    return component


##############################################################################
# Read input from spreadsheets
#
# Downloading a zipfile of xlsx files from Google Drive is most convenient
# but it's better to check tsv into git.


def read_single_sheet(path, name):
    """ Read an xlsx, csv or tsv from a zipfile or directory
    """
    from zipfile import ZipFile

    if path.endswith('.xlsx'):
        return xlreader.DictReader(open(path, 'rb'), sheetname=name)

    if path.endswith('.zip'):
        zf = ZipFile(path)
        names = zf.namelist()
        def open(n, mode):
            return zf.open(n, 'r')
        def exists(n):
            return n in names

    elif os.path.isdir(path):
        def exists(n):
            return os.path.exists(os.path.join(path, name))

    if exists(name + '.xlsx'):
        stream = open(name + '.xlsx', 'rb')
        return read_xl(stream)

    if exists(name + '.tsv'):
        stream = open(name + '.tsv', 'rb')
        return read_tsv(stream)

    if exists(name + '.csv'):
        stream = open(name + '.csv', 'rb')
        return read_csv(stream)

    raise ValueError("Unable to find %r in %s" % name, path)


def read_xl(stream):
    import xlreader
    return xlreader.DictReader(stream)


def read_tsv(stream):
    import csv
    return csv.DictReader(stream, delimiter='\t', quoting=csv.QUOTE_NONE)


def read_csv(stream):
    import csv
    return csv.DictReader(stream)


##############################################################################
# Posting json
#
# This would a one liner except for logging


def post(testapp, item_type, phase):
    base_url = TYPE_URL[item_type]
    if phase == 2:
        base_url = base_url + '{uuid}'

    def component(rows):
        for row in rows:
            if not row.get('_skip') and not row.get('_errors'):
                # Keys with leading underscores are for communicating between
                # sections
                value = row['_value'] = {
                    k: v for k, v in row.iteritems() if not k.startswith('_')
                }
                # Possibly 
                url = row['_url'] = base_url.format(uuid=row['uuid'])
                row['_response'] = testapp.post_json(url, value, status='*')

            yield row

    return component


##############################################################################
# Logging


def trim(value):
    """ Shorten excessively long fields in error log
    """
    if isinstance(value, dict):
        return {k: trim(v) for k, v in value.iteritems()}
    if isinstance(value, list):
        return [trim(v) for v in value]
    if isinstance(value, basestring) and len(value) > 160:
        return value[:77] + '...' + value[-80:]
    return value


def pipeline_logger(item_type, phase):
    def component(rows):
        created = 0
        updated = 0
        errors = 0
        skipped = 0
        for index, row in enumerate(rows):
            row_number = index + 2  # header row
            count = index + 1
            res = row.get('_response')

            if res is None:
                _skip = row.get('_skip')
                _errors = row.get('_errors')
                if row.get('_skip'):
                    skipped += 1
                elif _errors:
                    errors += 1
                    logger.error('%s row %d: Error PROCESSING: %s\n%r\n' % (item_type, row_number, _errors, trim(row)))
                yield row
                continue

            url = row.get('_url')
            uuid = row.get('uuid')

            if res.status_int == 200:
                updated += 1
                logger.debug('UPDATED: %s' % url)

            if res.status_int == 201:
                created += 1
                logger.debug('CREATED: %s' % res.location)

            if res.status_int == 409:
                logger.error('CONFLICT: %r' % res.json['detail'])

            if res.status_int == 422:
                logger.error('VALIDATION FAILED: %r' % trim(res.json['errors']))

            if res.status_int // 100 == 4:
                errors += 1
                logger.error('%s row %d: %s (%s)\n%r\n' % (item_type, row_number, res.status, url, trim(row['_value'])))

            yield row

        loaded = created + updated 
        logger.info('Loaded %d of %d %s (phase %s). CREATED: %d, UPDATED: %d, SKIPPED: %d, ERRORS: %d' % (
             loaded, count, item_type, phase, created, updated, skipped, errors))

    return component


##############################################################################
# Attachments


def find_doc(docsdir, filename):
    path = None
    for dirpath in docsdir:
        candidate = os.path.join(dirpath, filename)
        if not os.path.exists(candidate):
            continue
        if path is not None:
            msg = 'Duplicate filenames: %s, %s' % (path, candidate)
            raise ValueError(msg)
        path = candidate
    if path is None:
        raise ValueError('File not found: %s' % filename)
    return path


def attachment(path):
    """ Create an attachment upload object from a filename

    Embeds the attachment as a data url.
    """
    import mimetypes
    from PIL import Image
    from base64 import b64encode

    filename = os.path.basename(path)
    mime_type, encoding = mimetypes.guess_type(filename)

    with open(path, 'rb') as stream:
        attach = {
            'download': filename,
            'type': mime_type,
            'href': 'data:%s;base64,%s' % (mime_type, b64encode(stream.read()))
        }

        if mime_type in ('application/pdf', 'text/plain'):
            return attach

        major, minor = mime_type.split('/')

        if major == 'image' and minor in ('png', 'jpeg', 'gif', 'tiff'):
            # XXX we should just convert our tiffs to pngs
            stream.seek(0, 0)
            im = Image.open(stream)
            im.verify()
            if im.format != minor.upper():
                msg = "Image file format %r does not match extension for %s"
                raise ValueError(msg % (im.format, filename))

            attach['width'], attach['height'] = im.size
            return attach

    raise ValueError("Unknown file type for %s" % filename)


##############################################################################
# Pipelines


def combine(source, pipeline):
    """ Construct a combined generator from a source and pipeline
    """
    return reduce(lambda x, y: y(x), pipeline, source)


def process(rows):
    """ Pull rows through the pipeline
    """
    for row in rows:
        pass


def get_pipeline(testapp, docsdir, test_only, item_type, phase):
    pipeline = [
        cast_row_values,
        remove_keys_with_empty_value,
        skip_test_column_value_skip,
        filter_test_only(test_only),
        skip_rows_missing_all_keys('uuid'),
        remove_keys('schema_version'),
        remove_keys_with_unknown_value_except_for('lot_id'),
        remove_keys('test'),
        add_attachment(docsdir),
    ]
    if phase == 1:
        pipeline.extend(PIPELINES.get(item_type, []))
    else:
        pipeline.extend(UPDATE_PIPELINES.get(item_type, []))
    pipeline.extend([
        post(testapp, item_type, phase),
        pipeline_logger(item_type, phase),
    ])
    return pipeline


# Additional pipeline sections for item types

PIPELINES = {
    'colleague': [
        remove_keys('lab', 'submits_for'),
    ],
    'biosample': [
        remove_keys('derived_from', 'contained_in'),
    ],
    'experiment': [
        remove_keys('files', 'possible_controls'),
    ],
    'replicate': [
        # TODO flowcell_details parsing.
        remove_keys('flowcell_details'),
    ],
}


##############################################################################
# Update pipelines
#
# A second pass is required to cope with reference cycles. Only rows with
# filtered out keys are updated.


UPDATE_PIPELINES = {
    'colleague': [
        skip_rows_missing_all_keys('lab', 'submits_for'),
    ],
    'biosample': [
        skip_rows_missing_all_keys('derived_from', 'contained_in'),
    ],
    'experiment': [
        skip_rows_missing_all_keys('files', 'possible_controls'),
    ],
}


def load_all(testapp, filename, docsdir, test=False):
    import pdb
    import sys
    import traceback
    try:
        for item_type in ORDER:
            source = read_single_sheet(filename, item_type)
            pipeline = get_pipeline(testapp, docsdir, test, item_type, 1)
            process(combine(source, pipeline))

        for item_type in ORDER:
            if item_type not in UPDATE_PIPELINES:
                continue
            source = read_single_sheet(filename, item_type)
            pipeline = get_pipeline(testapp, docsdir, test, item_type, 2)
            process(combine(source, pipeline))
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
