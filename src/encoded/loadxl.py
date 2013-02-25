from PIL import Image
from base64 import b64encode
import datetime
import logging
import mimetypes
import os.path
import xlrd
# http://www.lexicon.net/sjmachin/xlrd.html

logger = logging.getLogger('encoded')

TYPE_URL = {
     'organism': '/organisms/',
     'source': '/sources/',
     'target': '/targets/',
     'antibody_lot': '/antibody-lots/',
     'validation': '/validations/',
     'antibody_approval': '/antibodies/',
     'donor': '/donors/',
     'document': '/documents/',
     'biosample': '/biosamples/',
     'document':  '/documents/',
     'submitter': '/submitters/',
     'colleague': '/users/',
     'lab': '/labs/',
     'award': '/awards/',
    ##{ 'institute': '/institutes/'),
   }


def resolve_dotted(value, name):
    for key in name.split('.'):
        value = value[key]
    return value


def convert(type_, value):
    if type_ is None:
        return value
    if type_ is datetime.date:
        return datetime.date(*value[:3]).isoformat()
    elif type_ is datetime.datetime:
        return datetime.datetime(*value).isoformat()
    else:
        return type_(value)


def cell_value(sheet, row, col, hint=None):
    if hint is None:
        hint = {}
    cell = sheet.cell(row, col)
    ctype = cell.ctype
    value = cell.value
    type_ = hint.get('type')

    if ctype == xlrd.XL_CELL_ERROR:
        raise ValueError((row, col, repr(cell)))

    elif ctype == xlrd.XL_CELL_BOOLEAN:
        if type_ is None:
            type_ = bool

    elif ctype == xlrd.XL_CELL_NUMBER:
        if type_ is None:
            type_ = int if value.is_integer() else float

    elif ctype == xlrd.XL_CELL_DATE:
        value = xlrd.xldate_as_tuple(value, sheet.book.datemode)
        if type_ is None:
            if value[3:] == (0, 0, 0):
                type_ = datetime.date
            else:
                type_ = datetime.datetime

    elif ctype == xlrd.XL_CELL_TEXT:
        value = value.strip()
        if value == 'null':
            value = None
        elif value == '':
            value = None

    # Empty cell
    elif ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        value = None

    else:
        raise ValueError((row, col, repr(cell), 'Unknown cell type.'))

    return convert(type_, value)


def iter_rows(sheet, headers=None, hints=None, start=1):
    if hints is None:
        hints = {}
    if headers is None:
        headers = [sheet.cell_value(0, col).lower().strip() for col in range(sheet.ncols)]
    for row in xrange(start, sheet.nrows):
        yield dict((name, cell_value(sheet, row, col, hints.get(name)))
            for col, name in enumerate(headers) if name)


def extract(filename, sheets):
    alldata = {}
    book = xlrd.open_workbook(filename)
    for name in sheets:
        data = alldata[name] = {}
        sheet = book.sheet_by_name(name)
        for row in iter_rows(sheet):
            try:
                # cricket method
                uuid = row.pop('%s_uuid' % name)
            except KeyError:
                # drew method
                try:
                    uuid = row.pop('guid')
                except KeyError:
                    # esther method, exceept where she put in extraneious (uuid)
                    uuid = row.pop('%s_no' % name)

            if not uuid:
                continue
            row['_uuid'] = uuid
            data[uuid] = row
    return alldata


def value_index(data, attribute):
    index = {}
    for uuid, value in data.iteritems():
        index_value = resolve_dotted(value, attribute)
        assert index_value not in index, index_value
        index[index_value] = uuid
    return index


def multi_index(data, attribute):
    index = {}
    for uuid, value in data.iteritems():
        index_value = resolve_dotted(value, attribute)
        index.setdefault(index_value, []).append(uuid)
    return index


def tuple_index(data, *attrs):
    index = {}
    for uuid, value in list(data.iteritems()):
        index_value = tuple(resolve_dotted(value, attr) for attr in attrs)
        if index_value in index:
            logger.warn('Duplicate values for %s, %s: %r' % (index[index_value], uuid, index_value))
            del[data[uuid]]
        else:
            index[index_value] = uuid
    return index


def multi_tuple_index(data, *attrs):
    index = {}
    for uuid, value in data.iteritems():
        index_value = tuple(resolve_dotted(value, attr) for attr in attrs)
        index.setdefault(index_value, []).append(uuid)
    return index


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


def post_collection(testapp, alldata, content_type):
    url = TYPE_URL[content_type]
    collection = alldata[content_type]
    nload = 0
    for uuid, value in list(collection.iteritems()):
        try:
            testapp.post_json(url, value, status=201)
            nload += 1
        except Exception as e:
            logger.warn('Error submitting %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, value))
            del alldata[content_type][uuid]
            continue
    logger.info('Loaded %d %s out of %d' % (nload, content_type, len(collection)))


def load_all(testapp, filename, docsdir):
    sheets = [content_type for content_type in TYPE_URL]
    alldata = extract(filename, sheets)

    content_type = 'submitter'
    post_collection(testapp, alldata, content_type)
    # hacked because we don't really have grant/award data
    submitter_index = multi_tuple_index(alldata['submitter'], 'last_name', 'lab_name')
    ### note needs first name too, eventually!!!

    content_type = 'colleague'
    post_collection(testapp, alldata, content_type)
    ##colleague_index = tuple_index(alldata['colleague'], 'last_name', 'first_name')

    content_type = 'lab'
    post_collection(testapp, alldata, content_type)
    ##lab_index = value_index(alldata['lab'], 'lab_name')

    content_type = 'award'
    post_collection(testapp, alldata, content_type)
    ##award_index = multi_index(alldata['award'], 'pi_last_name')

    content_type = 'organism'
    organism_index = value_index(alldata[content_type], 'organism_name')

    content_type = 'donor'
    post_collection(testapp, alldata, content_type)

    content_type = 'source'
    post_collection(testapp, alldata, content_type)
    source_index = value_index(alldata[content_type], 'source_name')

    content_type = 'biosample'
    post_collection(testapp, alldata, content_type)

    content_type = 'document'
    post_collection(testapp, alldata, content_type)

    content_type = 'target'
    for uuid, value in list(alldata[content_type].iteritems()):
        original = value.copy()
        try:
            value['organism_uuid'] = organism_index[value.pop('organism_name')]
            aliases = value.pop('target_aliases') or ''
            alias_source = value.pop('target_alias_source')
            value['dbxref'] = [
                {'db': alias_source, 'id': alias.strip()}
                for alias in aliases.split(';') if alias]

            creator = value.get('created_by', None)
            pi = value.get('lab_pi', None)

            try:
                submitter_uuids = submitter_index[(creator, pi)]
            except KeyError:
                raise ValueError('No submitter found for target: %s (%s)' % (creator, pi))

            value['creator_uuids'] = []
            for submitter_uuid in submitter_uuids:
                if alldata['submitter'].get(submitter_uuid, None) is None:
                    logger.warning('Missing/skipped submitter reference %s for target: %s' % (submitter_uuid, uuid))
                else:
                    value['creator_uuids'].append(submitter_uuid)

        except Exception as e:
            logger.warn('Error processing %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, original))
            del alldata[content_type][uuid]
            continue

    post_collection(testapp, alldata, content_type)
    target_index = tuple_index(alldata[content_type], 'target_label', 'organism_uuid')

    content_type = 'antibody_lot'
    for uuid, value in list(alldata[content_type].iteritems()):
        original = value.copy()
        try:
            source = value.pop('source')
            try:
                value['source_uuid'] = source_index[source]
            except KeyError:
                raise ValueError('Unable to find source: %s' % source)
            aliases = value.pop('antibody_alias') or ''
            alias_source = value.pop('antibody_alias_source')
            value['dbxref'] = [
                {'db': alias_source, 'id': alias.strip()}
                for alias in aliases.split(';') if alias]

            submitter = value.get('submitted_by', None)
            pi = value.get('submitted_by_pi', None)
            try:
                submitter_uuids = submitter_index[(submitter, pi)]
            except KeyError:
                raise ValueError('No submitter found for antibody-lot: %s (%s)' % (submitter, pi))

            value['submitter_uuids'] = []
            for submitter_uuid in submitter_uuids:
                if alldata['submitter'].get(submitter_uuid, None) is None:
                    logger.warning('Missing/skipped submitter reference %s for source: %s' % (submitter_uuid, uuid))
                else:
                    value['submitter_uuids'].append(submitter_uuid)

        except Exception as e:
            logger.warn('Error processing %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, original))
            del alldata[content_type][uuid]
            continue

    post_collection(testapp, alldata, 'antibody_lot')
    antibody_lot_index = tuple_index(alldata['antibody_lot'], 'product_id', 'lot_id')

    content_type = 'validation'
    for uuid, value in list(alldata[content_type].iteritems()):
        original = value.copy()
        try:
            if value['antibody_lot_uuid'] is None:
                raise ValueError('Missing antibody_lot_uuid')
            try:
                organism_uuid = organism_index[value.pop('organism_name')]
                key = (value.pop('target_label'), organism_uuid)
                value['target_uuid'] = target_index[key]
            except KeyError:
                raise ValueError('Unable to find target: %s' % key)

            filename = value.pop('document_filename')
            stream = open(os.path.join(docsdir, filename), 'rb')
            _, ext = os.path.splitext(filename.lower())
            if ext in ('.png', '.jpg', '.tiff'):
                value['document'] = image_data(stream, filename)
            elif ext == '.pdf':
                mime_type = 'application/pdf'
                value['document'] = {
                    'download': filename,
                    'type': mime_type,
                    'href': data_uri(stream, mime_type),
                    }
            else:
                raise ValueError("Unknown file type for %s" % filename)
        except Exception as e:
            logger.warn('Error processing %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, original))
            del alldata[content_type][uuid]
            continue

    post_collection(testapp, alldata, content_type)
    # validation_index = multi_tuple_index(alldata['validation'], 'antibody_lot_uuid', 'target_label', 'organism_name')
    validation_index = multi_index(alldata[content_type], 'document.download')

    content_type = 'antibody_approval'
    for uuid, value in list(alldata[content_type].iteritems()):
        original = value.copy()
        try:
            try:
                value['antibody_lot_uuid'] = antibody_lot_index[(value.pop('antibody_product_id'), value.pop('antibody_lot_id'))]
            except KeyError:
                raise ValueError('Missing/skipped antibody_lot reference')

            value['validation_uuids'] = []
            filenames = [v.strip() for v in (value.pop('validation_filenames') or '').split(';') if v]
            for filename in filenames:
                validation_uuids = validation_index.get(filename, [])
                for validation_uuid in validation_uuids:
                    if alldata['validation'].get(validation_uuid, None) is None:
                        logger.warn('Missing/skipped validation reference %s for antibody_approval: %s' % (validation_uuid, uuid))
                    else:
                        value['validation_uuids'].append(validation_uuid)
            try:
                organism_uuid = organism_index[value.pop('organism_name')]
                value['target_uuid'] = target_index[(value.pop('target_label'), organism_uuid)]
            except KeyError:
                raise ValueError('Missing/skipped target reference')

        except Exception as e:
            logger.warn('Error processing %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, original))
            del alldata[content_type][uuid]
            continue

    post_collection(testapp, alldata, content_type)
