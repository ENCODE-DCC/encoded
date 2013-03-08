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
                if col.find('_list') < 0:
                    continue
                row[col] = [v.strip() for v in (str(value) or '').split(';') if v]

            data[uuid] = row
        alldata['COUNTS'][name] = len(data.keys())
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

    try:
        try:
            data['submitter_uuid'] = indices['email'][fks['email']]
        except:
            data['submitter_uuid'] = indices['colleague'][fks['last_name']]

        try:
            data['lab_uuid'] = indices['lab_name'][fks['lab_name']]
        except:
            data['lab_uuid'] = indices['lab_pi'][fks['pi_last_name']]

        try:
            data['award_uuid'] = indices['award_id'][fks['award_no']]
        except:
            data['award_uuid'] = indices['award'][(fks['pi_last_name'], fks['project'])]

    except Exception as ef:
        raise ValueError('No submitter/lab found for %s: %s due to %s' %
                        (dtype, fks, ef))


def load_all(testapp, filename, docsdir, test=False):
    sheets = [content_type for content_type in TYPE_URL]
    alldata = extract(filename, sheets, test=test)

    indices = IndexContainer().indices

    content_type = 'award'
    post_collection(testapp, alldata, content_type)
    award_id_index = value_index(alldata['award'], 'number')
    award_index = tuple_index(alldata['award'], 'pi_last_name', 'project')
    indices['award_id'] = award_id_index
    indices['award'] = award_index

    content_type = 'lab'
    for uuid, value in list(alldata[content_type].iteritems()):
        try:
            assert type(value) == dict
        except:
            raise AttributeError("Bad lab: %s: %s" % (uuid, value))
        original = value.copy()
        value['pi_name'] = value.get('name', '').split('.')[1]
        ## no error trapping!

        value['award_uuids'] = []
        for award_id in value.get('award_number_list', []):
            award_uuid = indices['award_id'].get(award_id)  # singletons???
            if alldata['award'].get(award_uuid, None) is None:
                logger.warn('Missing/skipped award reference %s for lab: %s' % (award_uuid, uuid))
            else:
                value['award_uuids'].append(award_uuid)

        if not value['award_uuids']:
            logger.warn('PROCESSING %s %s: (no awards) Value:\n%r\n' % (content_type, uuid, original))
            #del alldata[content_type][uuid]
            continue

    post_collection(testapp, alldata, content_type)
    lab_index = value_index(alldata['lab'], 'name')
    lab_pi_index = value_index(alldata['lab'], 'pi_name')
    ## should actually use the tuple_index if we had all 3 parts of lab name.
    indices['lab_pi'] = lab_pi_index
    indices['lab_name'] = lab_index

    content_type = 'colleague'
    for uuid, value in list(alldata[content_type].iteritems()):
        try:
            assert type(value) == dict
        except:
            raise AttributeError("Bad colleague: %s: %s" % (uuid, value))
        original = value.copy()

        value['lab_uuids'] = []
        for lab_name in value.get('lab_name_list', []):
            lab_uuid = indices['lab_name'].get(lab_name)  # singletons???
            if alldata['lab'].get(lab_uuid, None) is None:
                logger.warn('Missing/skipped lab reference %s for lab: %s' % (lab_uuid, uuid))
            else:
                value['lab_uuids'].append(lab_uuid)

        if not value['lab_uuids']:
            logger.warn('PROCESSING %s %s: (no labs) Value:\n%r\n' % (content_type, uuid, original))
            #del alldata[content_type][uuid]
            continue


    post_collection(testapp, alldata, content_type)
    colleague_index = value_index(alldata['colleague'], 'last_name')
    email_index = value_index(alldata['colleague'], 'email')
    indices['colleague'] = colleague_index
    indices['email'] = email_index

    content_type = 'organism'
    for uuid, value in list(alldata[content_type].iteritems()):
        try:
            value['taxon_id'] = int(value['taxon_id'])
        except Exception as e:
            logger.warn('Error PROCESSING %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, original))
            del alldata[content_type][uuid]
            continue
    post_collection(testapp, alldata, content_type)
    organism_index = value_index(alldata[content_type], 'organism_name')
    indices['organism'] = organism_index

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
            aliases = value.pop('target_aliases') or ''  # needs to be _list!
            alias_source = value.pop('target_alias_source')
            value['dbxref'] = [
                {'db': alias_source, 'id': alias.strip()}
                for alias in aliases.split(';') if alias]

            value = assign_submitter(value, content_type, indices,
                                     {'email': value.pop('submitted_by_colleague_email'),
                                      'lab_name': value.pop('submitted_by_lab_name'),
                                      'award_no': value.pop('submitted_by_award_number')
                                     }
                                    )

        except Exception as e:
            logger.warn('Error PROCESSING %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, original))
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

            assign_submitter(value, content_type, indices,
                                    {'email': value.pop('submitted_by_colleague_email'),
                                      'lab_name': value.pop('submitted_by_lab_name'),
                                      'award_no': value.pop('submitted_by_award_number')
                                     }
                                    )


        except Exception as e:
            logger.warn('Error PROCESSING %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, original))
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
            organism_name = value.pop('organism_name')
            try:
                organism_uuid = organism_index[organism_name]
            except KeyError:
                raise ValueError('Unable to find organism: %s' % organism_name)
            key = (value.pop('target_label'), organism_uuid)
            try:
                value['target_uuid'] = target_index[key]
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
                             { 'last_name': value.pop('submitted_by'),
                               'pi_last_name': value.get('submitted_by_pi', None),
                               'project': value.pop('validated_by', None)
                             }
                            )

            check_lot = alldata['antibody_lot'][value['antibody_lot_uuid']]
            # should raise key errors if not present.
        except Exception as e:
            logger.warn('Error PROCESSING %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, original))
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
            logger.warn('Error PROCESSING %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, original))
            del alldata[content_type][uuid]
            continue

    post_collection(testapp, alldata, content_type)
