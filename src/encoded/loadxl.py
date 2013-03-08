from PIL import Image
from base64 import b64encode
import datetime
import logging
import mimetypes
import os.path
import xlrd
# http://www.lexicon.net/sjmachin/xlrd.html

logger = logging.getLogger('encoded')
logger.setLevel(logging.WARNING)  #doesn't work to shut off sqla INFO

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
    'colleague': '/users/',
    'lab': '/labs/',
    'award': '/awards/',
    ##{ 'institute': '/institutes/'),
}


class IndexContainer:
    indices = {}


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
    elif ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) or value == 'NULL':
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


def extract(filename, sheets, test=False):
    alldata = {
        'COUNTS': {}
    }
    book = xlrd.open_workbook(filename)
    for name in sheets:
        data = alldata[name] = {}
        try:
            sheet = book.sheet_by_name(name)
        except xlrd.XLRDError, e:
            logging.warn(e)
            alldata['COUNTS'][name] = 0
            continue

        for row in iter_rows(sheet):
            if test:
                try:
                    if not row.pop('test'):
                        continue
                except KeyError:
                    ## row doesn't have test marking assume it's to be always loaded
                    pass
            try:
                # cricket method
                uuid = row.pop('%s_uuid' % name)
            except KeyError:
                # new method
                try:
                    uuid = row.pop('uuid')
                except KeyError:
                    uuid = None

            if not uuid:
                continue
            row['_uuid'] = uuid

            for col, value in row.iteritems():
                if col.find('_list') < 0: continue
                if value == 'NULL': continue # otherwise we get ['NULL']
                row[col] = [v.strip() for v in (str(value) or '').split(';') if v]

            data[uuid] = row
        alldata['COUNTS'][name] = len(data.keys())
    return alldata


def value_index(data, attribute):
    index = {}
    for uuid, value in data.iteritems():
        index_value = resolve_dotted(value, attribute)
        if not index_value or index_value == 'NULL': continue
        assert index_value not in index, index_value
        index[index_value] = uuid
    return index


def multi_index(data, attribute):
    index = {}
    for uuid, value in data.iteritems():
        index_value = resolve_dotted(value, attribute)
        index.setdefault(index_value, []).append(uuid)
    return index


def tuple_index(data, tup):
    index = {}
    for uuid, value in list(data.iteritems()):
        index_value = tuple(resolve_dotted(value, attr) for attr in tup)
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
            res = testapp.post_json(url, value, status=[201, 422])
            nload += 1
        except Exception as e:
            logger.warn('Error SUBMITTING %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, value))
            del alldata[content_type][uuid]
        else:
            if res.status_code == 422:
                logger.warn('Error VALIDATING %s %s: %r. Value:\n%r\n' % (content_type, uuid, res.json['errors'], value))
                del alldata[content_type][uuid]
    logger.warn('Loaded %d %s out of %d' % (nload, content_type, alldata['COUNTS'][content_type]))


def assign_submitter(data, dtype, indices, fks):

    '''
    if not fks.get('award_no', None):
        if not fks.get('project', None):
            raise KeyError
        if not fks.get('pi_last_name', None):
            fks['pi_last_name'] = fks.get('project', None)

        try:
            if not fks.get('last_name', None):
                fks['last_name'] = fks.get('project', None)
        except Exception as e:
            raise ValueError('Bad submitter keys %s: %s due to: %s' %
                        (dtype, fks, e))
    '''

    try:
        data['submitter_uuid'] = indices['colleague'][fks['email']]
        data['lab_uuid'] = indices['lab'][fks['lab_name']]
        data['award_uuid'] = indices['award'][fks['award_no']]

    except Exception as ef:
        raise ValueError('No submitter/lab found for %s: %s due to %s' %
                        (dtype, fks, ef))


def parse_decorator_factory(content_type, index_type):

    def parse_sheet(parse_type):

        def wrapped(testapp, alldata, indices, content_type, docsdir):

            for uuid, value in list(alldata[content_type].iteritems()):

                try:  # one big error handle
                    assert type(value) == dict
                    original = value.copy()
                    # the wrapped function
                    parse_type(testapp, alldata, content_type, indices, uuid, value, docsdir)

                except Exception as e:
                    logger.warn('PROCESSING %s %s: %s Value:\n%r\n' % (content_type, uuid, e, original))
                    del alldata[content_type][uuid]
                    continue

            post_collection(testapp, alldata, content_type)
            for itype, cols in list(index_type.iteritems()):
                if itype == 'multi':
                    my_index = multi_index(alldata[content_type], cols)
                elif itype == 'tuple':
                    my_index = tuple_index(alldata[content_type], cols)
                else:
                    my_index = value_index(alldata[content_type], cols)
                indices[content_type] = my_index  # one each

        return wrapped

    return parse_sheet


@parse_decorator_factory('award', {'value': 'number'})
def parse_award(testapp, alldata, content_type, indices, uuid, value, docsdir):
    pass


@parse_decorator_factory('lab', {'value': 'name'})
def parse_lab(testapp, alldata, content_type, indices, uuid, value, docsdir):

    value['award_uuids'] = []
    for award_id in value.get('award_number_list', []):
        award_uuid = indices['award'].get(award_id)  # singletons???
        if alldata['award'].get(award_uuid, None) is None:
            logger.warn('Missing/skipped award reference %s for lab: %s' % (award_uuid, uuid))
        else:
            value['award_uuids'].append(award_uuid)


@parse_decorator_factory('colleague', {'value': 'email'})
def parse_colleague(testapp, alldata, content_type, indices, uuid, value, docsdir):

    value['lab_uuids'] = []
    for lab_name in value.get('lab_name_list', []):
        lab_uuid = indices['lab'].get(lab_name)  # singletons???
        if alldata['lab'].get(lab_uuid, None) is None:
            logger.warn('Missing/skipped lab reference %s for lab: %s' % (lab_uuid, uuid))
        else:
            value['lab_uuids'].append(lab_uuid)


@parse_decorator_factory('organism', {'value': 'organism_name'})
def parse_organism(testapp, alldata, content_type, indices, uuid, value, docsdir):
    value['taxon_id'] = int(value['taxon_id'])


@parse_decorator_factory('source', {'value': 'source_name'})
def parse_source(testapp, alldata, content_type, indices, uuid, value, docsdir):
    pass


@parse_decorator_factory('target', {'tuple': ('target_label', 'organism_uuid')})
def parse_target(testapp, alldata, content_type, indices, uuid, value, docsdir):

    value['organism_uuid'] = indices['organism'][value.pop('organism_name')]
    aliases = value.pop('target_aliases') or ''  # needs to be _list!
    alias_source = value.pop('target_alias_source')
    value['dbxref'] = [
        {'db': alias_source, 'id': alias.strip()}
        for alias in aliases.split(';') if alias]

    value = assign_submitter(value, content_type, indices,
                             {
                             'email': value.pop('submitted_by_colleague_email'),
                             'lab_name': value.pop('submitted_by_lab_name'),
                             'award_no': value.pop('submitted_by_award_number')
                             }
                             )


@parse_decorator_factory('antibody_lot', {'tuple': ('product_id', 'lot_id')})
def parse_antibody_lot(testapp, alldata, content_type, indices, uuid, value, docsdir):

    source = value.pop('source')
    try:
        value['source_uuid'] = indices['source'][source]
    except KeyError:
        raise ValueError('Unable to find source: %s' % source)
    aliases = value.pop('antibody_alias') or ''
    alias_source = value.pop('antibody_alias_source')
    value['dbxref'] = [
        {'db': alias_source, 'id': alias.strip()}
        for alias in aliases.split(';') if alias]

    assign_submitter(value, content_type, indices,
                     {
                     'email': value.pop('submitted_by_colleague_email'),
                     'lab_name': value.pop('submitted_by_lab_name'),
                     'award_no': value.pop('submitted_by_award_number')
                     }
                     )


@parse_decorator_factory('validation', {'multi': 'document.download'})
def parse_validation(testapp, alldata, content_type, indices, uuid, value, docsdir):

        organism_name = value.pop('organism_name')
        try:
            organism_uuid = indices['organism'][organism_name]
        except KeyError:
            raise ValueError('Unable to find organism: %s' % organism_name)
        key = (value.pop('target_label'), organism_uuid)
        try:
            value['target_uuid'] = indices['target'][key]
        except KeyError:
            raise ValueError('Unable to find target: %r' % (key,))

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

        assign_submitter(value, content_type, indices,
                         {
                         'email': value.pop('submitted_by_colleague_email'),
                         'lab_name': value.pop('submitted_by_lab_name'),
                         'award_no': value.pop('submitted_by_award_number')
                         }
                         )
        try:
            check_lot = alldata['antibody_lot'][value['antibody_lot_uuid']]
        except KeyError:
            raise ValueError('Antibody lot %s not present' % (value['antibody_lot_uuid']))


@parse_decorator_factory('antibody_approval', {})
def parse_antibody_approval(testapp, alldata, content_type, indices, uuid, value, docsdir):

    try:
        value['antibody_lot_uuid'] = indices['antibody_lot'][(value.pop('antibody_product_id'), value.pop('antibody_lot_id'))]
    except KeyError:
        raise ValueError('Missing/skipped antibody_lot reference')

    value['validation_uuids'] = []
    filenames = value.pop('validation_filenames_list')
    #[v.strip() for v in (value.pop('validation_filenames') or '').split(';') if v]
    # above should be renamed validation_filenames_list
    for filename in filenames:
        validation_uuids = indices['validation'].get(filename, [])
        for validation_uuid in validation_uuids:
            if alldata['validation'].get(validation_uuid, None) is None:
                logger.warn('Missing/skipped validation reference %s for antibody_approval: %s' % (validation_uuid, uuid))
            else:
                value['validation_uuids'].append(validation_uuid)
    try:
        organism_uuid = indices['organism'][value.pop('organism_name')]
        value['target_uuid'] = indices['target'][(value.pop('target_label'), organism_uuid)]
    except KeyError:
        raise ValueError('Missing/skipped target reference')

@parse_decorator_factory('donor', {'value': 'donor_id'})
def parse_donor(testapp, alldata, content_type, indices, uuid, value, docsdir):

    source_list = value.pop('alias_source_list')
    try:
        value['alias_source_uuids'] = [ indices['source'][source] for source in source_list ]
    except KeyError:
        return # just skip this error for now
        raise ValueError('Unable to find source: %s' % source)


def load_all(testapp, filename, docsdir, test=False):
    sheets = [content_type for content_type in TYPE_URL]
    alldata = extract(filename, sheets, test=test)

    indices = IndexContainer().indices

    parse_award(testapp, alldata, indices, 'award', docsdir)
    '''award_id_index = value_index(alldata['award'], 'number')
    award_index = tuple_index(alldata['award'], 'pi_last_name', 'project')
    indices['award_id'] = award_id_index
    indices['award'] = award_index
    '''

    parse_lab(testapp, alldata, indices, 'lab', docsdir)

    '''
    lab_index = value_index(alldata['lab'], 'name')
    lab_pi_index = value_index(alldata['lab'], 'pi_name')
    ## should actually use the tuple_index if we had all 3 parts of lab name.
    indices['lab_pi'] = lab_pi_index
    indices['lab_name'] = lab_index
    '''

    parse_colleague(testapp, alldata, indices, 'colleague', docsdir)

    '''
    colleague_index = value_index(alldata['colleague'], 'last_name')
    email_index = value_index(alldata['colleague'], 'email')
    indices['colleague'] = colleague_index
    indices['email'] = email_index
    '''

    parse_organism(testapp, alldata, indices, 'organism', docsdir)

    '''
    organism_index = value_index(alldata[content_type], 'organism_name')
    indices['organism'] = organism_index
    '''

    parse_source(testapp, alldata, indices, 'source', docsdir)

    '''
    source_index = value_index(alldata[content_type], 'source_name')
    '''

    parse_target(testapp, alldata, indices, 'target', docsdir)

    '''
    target_index = tuple_index(alldata[content_type], 'target_label', 'organism_uuid')
    '''

    parse_antibody_lot(testapp, alldata, indices, 'antibody_lot', docsdir)

    '''
    antibody_lot_index = tuple_index(alldata['antibody_lot'], 'product_id', 'lot_id')
    '''

    parse_validation(testapp, alldata, indices, 'validation', docsdir)

    '''
    validation_index = multi_tuple_index(alldata['validation'], 'antibody_lot_uuid', 'target_label', 'organism_name')
    validation_index = multi_index(alldata[content_type], 'document.download')
    '''

    parse_antibody_approval(testapp, alldata, indices, 'antibody_approval', docsdir)

    parse_donor(testapp, alldata, indices, 'donor', docsdir)
    '''
    content_type = 'document'
    post_collection(testapp, alldata, content_type)

    content_type = 'biosample'
    post_collection(testapp, alldata, content_type)

    '''

