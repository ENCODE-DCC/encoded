from PIL import Image
from base64 import b64encode
import datetime
import logging
import mimetypes
from pkg_resources import resource_stream
import xlrd
# http://www.lexicon.net/sjmachin/xlrd.html

logger = logging.getLogger('encoded')


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
            for col, name in enumerate(headers) if name is not None)


def extract(filename, sheets):
    alldata = {}
    book = xlrd.open_workbook(filename)
    for name in sheets:
        data = alldata[name] = {}
        sheet = book.sheet_by_name(name)
        for row in iter_rows(sheet):
            uuid = row['%s_uuid' % name]
            if not uuid:
                continue
            row['_uuid'] = uuid
            data[uuid] = row
    return alldata

TYPE_URL = [
    ('organism', '/organisms/'),
    ('source', '/sources/'),
    ('target', '/targets/'),
    ('antibody_lot', '/antibody-lots/'),
    ('validation', '/validations/'),
    ('antibody_approval', '/antibodies/'),
    ]


def value_index(data, attribute):
    index = {}
    for uuid, value in data.iteritems():
        index_value = value[attribute]
        assert index_value not in index, index_value
        index[index_value] = uuid
    return index


def multi_index(data, attribute):
    index = {}
    for uuid, value in data.iteritems():
        index_value = value[attribute]
        index.setdefault(index_value, []).append(uuid)
    return index


def tuple_index(data, *attrs):
    index = {}
    for uuid, value in data.iteritems():
        index_value = tuple(value[attr] for attr in attrs)
        assert index_value not in index, index_value
        index[index_value] = uuid
    return index


def multi_tuple_index(data, *attrs):
    index = {}
    for uuid, value in data.iteritems():
        index_value = tuple(value[attr] for attr in attrs)
        index.setdefault(index_value, []).append(uuid)
    return index


def image_data_uri(stream):
    im = Image.open(stream)
    im.verify()
    mime_type, _ = mimetypes.guess_type('name.%s' % im.format)
    stream.seek(0, 0)
    data = b64encode(stream.read())
    return 'data:%s;base64,%s' % (mime_type, data)


def load_all(testapp, filename):
    sheets = [content_type for content_type, url in TYPE_URL]
    alldata = extract(filename, sheets)

    organism_index = value_index(alldata['organism'], 'organism_name')
    source_index = value_index(alldata['source'], 'source_name')
    target_index = tuple_index(alldata['target'], 'target_label', 'organism_name')
    # validation_index = multi_tuple_index(alldata['validation'], 'antibody_lot_uuid', 'target_label', 'organism_name')
    validation_index = multi_index(alldata['validation'], 'document_filename')

    for uuid, value in alldata['target'].iteritems():
        value['organism_uuid'] = organism_index[value.pop('organism_name')]
        aliases = value.pop('target_aliases') or ''
        alias_source = value['target_alias_source']
        value['dbxref'] = [
            {'db': alias_source, 'id': alias.strip()}
            for alias in aliases.split(';')]

    for uuid, value in list(alldata['antibody_lot'].iteritems()):
        source = value.pop('source')
        try:
            value['source_uuid'] = source_index[source]
        except KeyError:
            logger.warn('Unable to find source: %s (%s)' % (source, uuid))
            del alldata['antibody_lot'][uuid]

    antibody_lot_index = tuple_index(alldata['antibody_lot'], 'product_id', 'lot_id')

    for uuid, value in alldata['validation'].iteritems():
        value['target_uuid'] = target_index[(value.pop('target_label'), value.pop('organism_name'))]
        filename = value.pop('document_filename')
        value['document'] = {
            'download': filename,
            'href': image_data_uri(resource_stream('encoded', 'tests/data/validation-docs/' + filename)),
            }

    for uuid, value in list(alldata['antibody_approval'].iteritems()):
        try:
            value['antibody_lot_uuid'] = antibody_lot_index[(value.pop('antibody_product_id'), value.pop('antibody_lot_id'))]
            #value['validation_uuids'] = validation_index.get((value['antibody_lot_uuid'], value['target_label'], value['organism_name']), [])
            value['validation_uuids'] = []
            filenames = (value.pop('validation_filenames') or '').split(';')
            for filename in filenames:
                validation_uuids = validation_index.get(filename, [])
                value['validation_uuids'].extend(validation_uuids)
            value['target_uuid'] = target_index[(value.pop('target_label'), value.pop('organism_name'))]
        except KeyError:
            logger.debug('Missing/skipped reference for antibody_approval: %s' % uuid)
            del alldata['antibody_approval'][uuid]

    for content_type, url in TYPE_URL:
        collection = alldata[content_type]
        for item in collection.itervalues():
            testapp.post_json(url, item, status=201)
