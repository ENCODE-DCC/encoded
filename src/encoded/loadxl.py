from .typedsheets import cast_row_values
from functools import reduce
import logging
import os.path

text = type(u'')

logger = logging.getLogger('encoded')
logger.setLevel(logging.INFO)  # doesn't work to shut off sqla INFO

ORDER = [
    'user',
    'award',
    'lab',
    'organism',
    'source',
    'target',
    'document',
    'antibody_lot',
    'antibody_characterization',
    'antibody_approval',
    'treatment',
    'construct',
    'construct_characterization',
    'rnai',
    'rnai_characterization',
    'talen',
    'mouse_donor',
    'fly_donor',
    'worm_donor',
    'human_donor',
    'donor_characterization',
    'biosample',
    'biosample_characterization',
    'platform',
    'library',
    'experiment',
    'replicate',
    'dataset',
    'publication',
    'software',
    'software_version',
    'analysis_step',
    'pipeline',
    'workflow_run',
    'analysis_step_run',
    'file',
    'quality_metric',
    'image',
    'page',
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


def remove_keys_with_empty_value(dictrows):
    for row in dictrows:
        yield {
            k: v for k, v in row.items()
            if k and v not in ('', None, [])
        }


##############################################################################
# Pipeline component factories


def warn_keys_with_unknown_value_except_for(*keys):
    def component(dictrows):
        for row in dictrows:
            for k, v in row.items():
                if k not in keys and text(v).lower() == 'unknown':
                    logger.warn('unknown %r for %s' % (k, row.get('uuid', '<empty uuid>')))
            yield row

    return component


def skip_rows_missing_all_keys(*keys):
    def component(dictrows):
        for row in dictrows:
            if not any(key in row for key in keys):
                row['_skip'] = True
            yield row

    return component


def skip_rows_with_all_key_value(**kw):
    def component(dictrows):
        for row in dictrows:
            if all(row[k] == v if k in row else False for k, v in kw.items()):
                row['_skip'] = True
            yield row

    return component


def skip_rows_without_all_key_value(**kw):
    def component(dictrows):
        for row in dictrows:
            if not all(row[k] == v if k in row else False for k, v in kw.items()):
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


def skip_rows_with_all_falsey_value(*keys):
    def component(dictrows):
        for row in dictrows:
            if all(not row[key] if key in row else False for key in keys):
                row['_skip'] = True
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
            except ValueError as e:
                row['_errors'] = repr(e)
            yield row

    return component


##############################################################################
# Read input from spreadsheets
#
# Downloading a zipfile of xlsx files from Google Drive is most convenient
# but it's better to check tsv into git.


def read_single_sheet(path, name=None):
    """ Read an xlsx, csv or tsv from a zipfile or directory
    """
    from zipfile import ZipFile
    from . import xlreader

    if name is None:
        root, ext = os.path.splitext(path)
        stream = open(path, 'rb')

        if ext == '.xlsx':
            return read_xl(stream)

        if ext == '.tsv':
            return read_csv(stream, dialect='excel-tab')

        if ext == '.csv':
            return read_csv(stream)

        if ext == '.json':
            return read_json(stream)

        raise ValueError('Unknown file extension for %r' % path)

    if path.endswith('.xlsx'):
        return cast_row_values(xlreader.DictReader(open(path, 'rb'), sheetname=name))

    if path.endswith('.zip'):
        zf = ZipFile(path)
        names = zf.namelist()

        if (name + '.xlsx') in names:
            stream = zf.open(name + '.xlsx', 'r')
            return read_xl(stream)

        if (name + '.tsv') in names:
            stream = zf.open(name + '.tsv', 'rU')
            return read_csv(stream, dialect='excel-tab')

        if (name + '.csv') in names:
            stream = zf.open(name + '.csv', 'rU')
            return read_csv(stream)

        if (name + '.json') in names:
            stream = zf.open(name + '.json', 'r')
            return read_json(stream)

    if os.path.isdir(path):
        root = os.path.join(path, name)

        if os.path.exists(root + '.xlsx'):
            stream = open(root + '.xlsx', 'rb')
            return read_xl(stream)

        if os.path.exists(root + '.tsv'):
            stream = open(root + '.tsv', 'rbU')
            return read_csv(stream, dialect='excel-tab')

        if os.path.exists(root + '.csv'):
            stream = open(root + '.csv', 'rbU')
            return read_csv(stream)

        if os.path.exists(root + '.json'):
            stream = open(root + '.json', 'rb')
            return read_json(stream)

    return []


def read_xl(stream):
    from . import xlreader
    return cast_row_values(xlreader.DictReader(stream))


def read_csv(stream, **kw):
    import csv
    return cast_row_values(csv.DictReader(stream, **kw))


def read_json(stream):
    import codecs
    import json
    utf8 = codecs.getreader('utf-8')
    obj = json.load(utf8(stream))
    if isinstance(obj, dict):
        return [obj]
    return obj


##############################################################################
# Posting json
#
# This would a one liner except for logging

def request_url(item_type, method):
    def component(rows):
        for row in rows:
            if method == 'POST':
                url = row['_url'] = '/' + item_type
                yield row
                continue

            if '@id' in row:
                url = row['@id']
                if not url.startswith('/'):
                    url = '/' + url
                row['_url'] = url
                yield row
                continue

            # XXX support for aliases
            for key in ['uuid', 'accession']:
                if key in row:
                    url = row['_url'] = '/' + row[key]
                    break
            else:
                row['_errors'] = ValueError('No key found. Need uuid or accession.')

            yield row

    return component

def make_request(testapp, item_type, method):
    json_method = getattr(testapp, method.lower() + '_json')

    def component(rows):
        for row in rows:
            if row.get('_skip') or row.get('_errors') or not row.get('_url'):
                continue

            # Keys with leading underscores are for communicating between
            # sections
            value = row['_value'] = {
                k: v for k, v in row.items() if not k.startswith('_') and not k.startswith('@')
            }

            url = row['_url']
            row['_response'] = json_method(url, value, status='*')

            yield row

    return component


##############################################################################
# Logging


def trim(value):
    """ Shorten excessively long fields in error log
    """
    if isinstance(value, dict):
        return {k: trim(v) for k, v in value.items()}
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
        count = 0
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
    import magic
    import mimetypes
    from PIL import Image
    from base64 import b64encode

    filename = os.path.basename(path)
    mime_type, encoding = mimetypes.guess_type(path)
    major, minor = mime_type.split('/')
    detected_type = magic.from_file(path, mime=True).decode('ascii')

    # XXX This validation logic should move server-side.
    if not (detected_type == mime_type or
            detected_type == 'text/plain' and major == 'text'):
        raise ValueError('Wrong extension for %s: %s' % (detected_type, filename))

    with open(path, 'rb') as stream:
        attach = {
            'download': filename,
            'type': mime_type,
            'href': 'data:%s;base64,%s' % (mime_type, b64encode(stream.read()).decode('ascii'))
        }

        if mime_type in ('application/pdf', 'text/plain', 'text/tab-separated-values'):
            # XXX Should use chardet to detect charset for text files here.
            return attach

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


def get_pipeline(testapp, docsdir, test_only, item_type, phase=None, method=None):
    pipeline = [
        skip_rows_with_all_key_value(test='skip'),
        skip_rows_with_all_key_value(_test='skip'),
        skip_rows_with_all_falsey_value('test') if test_only else noop,
        skip_rows_with_all_falsey_value('_test') if test_only else noop,
        remove_keys_with_empty_value,
        skip_rows_missing_all_keys('uuid', 'accession', '@id'),
        remove_keys('schema_version'),
        warn_keys_with_unknown_value_except_for(
            'lot_id', 'sex', 'life_stage', 'health_status', 'ethnicity',
            'strain_background', 'age',  # 'flowcell_details.machine',
        ),
        add_attachment(docsdir),
    ]
    if phase == 1:
        method = 'POST'
        pipeline.extend(PHASE1_PIPELINES.get(item_type, []))
    elif phase == 2:
        method = 'PUT'
        pipeline.extend(PHASE2_PIPELINES.get(item_type, []))

    pipeline.extend([
        request_url(item_type, method),
        remove_keys('uuid') if method in ('PUT', 'PATCH') else noop,
        make_request(testapp, item_type, method),
        pipeline_logger(item_type, phase),
    ])
    return pipeline


# Additional pipeline sections for item types

PHASE1_PIPELINES = {
    'user': [
        remove_keys('lab', 'submits_for'),
    ],
    'biosample': [
        remove_keys('derived_from', 'pooled_from'),
    ],
    'library': [
        remove_keys('spikeins_used'),
    ],
    'dataset': [
        remove_keys('related_files'),
    ],
    'experiment': [
        remove_keys('related_files', 'possible_controls'),
    ],
    'workflow_run': [
        remove_keys('input_files'),
    ],
}


##############################################################################
# Phase 2 pipelines
#
# A second pass is required to cope with reference cycles. Only rows with
# filtered out keys are updated.


PHASE2_PIPELINES = {
    'user': [
        skip_rows_missing_all_keys('lab', 'submits_for'),
    ],
    'biosample': [
        skip_rows_missing_all_keys('derived_from', 'pooled_from'),
    ],
    'library': [
        skip_rows_missing_all_keys('spikeins_used'),
    ],
    'experiment': [
        skip_rows_missing_all_keys('related_files', 'possible_controls'),
    ],
    'dataset': [
        skip_rows_missing_all_keys('related_files'),
    ],
    'workflow_run': [
        skip_rows_missing_all_keys('input_files'),
    ],
}


def load_all(testapp, filename, docsdir, test=False):
    for item_type in ORDER:
        try:
            source = read_single_sheet(filename, item_type)
        except ValueError:
            continue
        pipeline = get_pipeline(testapp, docsdir, test, item_type, phase=1)
        process(combine(source, pipeline))

    for item_type in ORDER:
        if item_type not in PHASE2_PIPELINES:
            continue
        try:
            source = read_single_sheet(filename, item_type)
        except ValueError:
            continue
        pipeline = get_pipeline(testapp, docsdir, test, item_type, phase=2)
        process(combine(source, pipeline))
