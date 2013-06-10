from PIL import Image
from base64 import b64encode
import datetime
import logging
import mimetypes
import os.path
import xlrd
# http://www.lexicon.net/sjmachin/xlrd.html

logger = logging.getLogger('encoded')
logger.setLevel(logging.WARN)  # doesn't work to shut off sqla INFO

TYPE_URL = {
    # TODO This has appears in 3 places... maybe it shoudl be configged
    'organism': '/organisms/',
    'source': '/sources/',
    'target': '/targets/',
    'antibody_lot': '/antibody-lots/',
    'validation': '/validations/',
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


class IndexContainer:
    indices = {}


def resolve_dotted(value, name):
    try:
        for key in name.split('.'):
         value = value[key]
        return value
    except KeyError:
        return None


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
        if value.lower() == 'null':
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

            dbxs = {}
            for col, value in row.iteritems():
                if col.find('_list') < 0: continue
                if not value:
                    val_list = []  # oh so clanky, but str(None) = 'None'
                else:
                    val_list = [v.strip() for v in (str(value) or '').split(';') if v]
                if col.find('dbxref') >= 0:
                    dbxs[col.split('_')[0]] = val_list
                else:
                    row[col] = val_list

            if dbxs: row['dbxref'] = dbxs
            if data.get(uuid, None) is None:
                data[uuid] = row
            else:
                logger.warn("Duplicate UUIDs for %s: (%s) first: %s" % (name, uuid, row))
        alldata['COUNTS'][name] = len(data.keys())
    return alldata


def value_index(data, attribute):
    index = {}
    for uuid, value in data.iteritems():
        index_value = resolve_dotted(value, attribute)
        if not index_value: continue
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


def post_all(testapp, alldata, content_type):
    url = TYPE_URL[content_type]
    collection = alldata[content_type].copy()
    nupdate = 0

    # first attempt to update all values
    for uuid, value in list(collection.iteritems()):
        value = dict((k, v) for k, v in value.iteritems() if v is not None)
        update_url = url+uuid+'/'
        try:
            res = testapp.post_json(update_url, value, status=[404, 200, 422])
        except Exception as e:
            logger.warn('Error UPDATING %s %s: %r. Value:\n%r\n' % (content_type, uuid, e, trim(value)))
        else:
            if res.status_code == 422:
                logger.warn('Error VALIDATING for UPDATE %s %s: %r. Value:\n%r\n' % (content_type, uuid, res.json['errors'], trim(value)))
                del alldata[content_type][uuid]
            elif res.status_code == 404:
                logger.info('%s %s could not be found for UPDATE, posting as new' % (content_type, uuid))
            elif res.status_code == 200:
                logger.info('%s %s UPDATED' % (content_type, uuid))
                nupdate += 1
                del collection[uuid]


    logger.warn('Updated %d %s out of %d' % (nupdate, content_type, alldata['COUNTS'][content_type]))

    # now create whatever's left
    post_collection(testapp, collection, url, alldata['COUNTS'][content_type]-nupdate)


def post_collection(testapp, collection, url, count):

    nload = 0
    for uuid, value in list(collection.iteritems()):
        value = dict((k, v) for k, v in value.iteritems() if v is not None)
        try:
            res = testapp.post_json(url, value, status=[201, 422])
            nload += 1
        except Exception as e:
            logger.warn('Error SUBMITTING NEW %s %s: %r. Value:\n%r\n' % (url, uuid, e, trim(value)))
            del collection[uuid]
        else:
            if res.status_code == 422:
                logger.warn('Error VALIDATING NEW %s %s: %r. Value:\n%r\n' % (url, uuid, res.json['errors'], trim(value)))
                del collection[uuid]
    logger.warn('Loaded NEW %d %s out of %d' % (nload, url, count))


def assign_submitter(data, dtype, indices, fks):

    try:
        data['submitter_uuid'] = indices['colleague'][fks['email']]
        data['lab_uuid'] = indices['lab'][fks['lab_name']]
        data['award_uuid'] = indices['award'][fks['award_no']]

    except Exception as ef:
        raise ValueError('No submitter/lab found for %s: %s due to %s' %
                        (dtype, fks, ef))


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

            post_all(testapp, alldata, content_type)
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
            logger.warn('Missing/skipped lab reference %s for colleague: %s' % (lab_uuid, uuid))
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
    '''value['dbxref'] = [
        {'db': alias_source, 'id': alias.strip()}
        for alias in aliases.split(';') if alias]
    '''
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
    '''aliases = value.pop('antibody_alias') or ''
    alias_source = value.pop('antibody_alias_source')
    value['dbxref'] = [
        {'db': alias_source, 'id': alias.strip()}
        for alias in aliases.split(';') if alias]
    '''
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

    value['document'] = check_document(docsdir, filename)
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
    validations = set([])
    for filename in filenames:
        validation_uuids = indices['validation'].get(filename, [])
        for validation_uuid in validation_uuids:
            val = alldata['validation'].get(validation_uuid, None)
            if val is None:
                logger.warn('Missing/skipped validation reference %s for antibody_approval: %s' % (validation_uuid, uuid))
            else:
                method = val['validation_method']
                if (filename, method) not in validations:
                    value['validation_uuids'].append(validation_uuid)
                    validations.add((filename, method))
                else:
                    pass
                    # frowny_gel is frowny because log files get clogged
                    #logger.warn('Duplicate method/validation skipped: %s %s for approval' % (filename, method))

    # make sure there are no duplicates
    assert len(set(value['validation_uuids'])) == len(value['validation_uuids'])

    try:
        organism_uuid = indices['organism'][value.pop('organism_name')]
        value['target_uuid'] = indices['target'][(value.pop('target_label'), organism_uuid)]
    except KeyError:
        raise ValueError('Missing/skipped target reference')


@parse_decorator_factory('donor', {'value': 'donor_id'})
def parse_donor(testapp, alldata, content_type, indices, uuid, value, docsdir):

    value['organism_uuid'] = indices['organism'][value.pop('organism')]
    source_list = value.pop('alias_source_list')
    try:
        value['alias_source_uuids'] = [indices['source'][source] for source in source_list]
    except KeyError:
        return  # just skip this error for now
        raise ValueError('Unable to find source: %s' % source)


@parse_decorator_factory('document', {'value': 'document_name'})
def parse_document(testapp, alldata, content_type, indices, uuid, value, docsdir):

    filename = value.pop('document_file_name')
    value['document'] = check_document(docsdir, filename)

    assign_submitter(value, content_type, indices,
                     {
                     'email': value.pop('submitted_by_colleague_email'),
                     'lab_name': value.pop('submitted_by_lab_name'),
                     'award_no': value.pop('submitted_by_award_number')
                     }
                     )


@parse_decorator_factory('treatment', {'value': 'treatment_name'})
def parse_treatment(testapp, alldata, content_type, indices, uuid, value, docsdir):

    try:
        value['duration'] = float(value['duration'])
    except (ValueError, TypeError):
        del value['duration']

    try:
        value['concentration'] = float(value['concentration'])
    except (ValueError, TypeError):
        del value['concentration']

    #import pdb; pdb.set_trace();
    value['document_uuids'] = []
    if value['treatment_document_list']:
        documents = value.pop('treatment_document_list')
        for doc in documents:
            try:
                document_uuid = indices['document'].get(doc, None)
                if alldata['document'].get(document_uuid, None) is None:
                    raise ValueError('Missing/skipped document reference %s for treatment: %s' % (doc, uuid))
                else:
                    value['document_uuids'].append(document_uuid)
            except KeyError:
                raise ValueError('Unable to find document for treatment: %s' % doc)


@parse_decorator_factory('construct', {'value': 'vector_name'})
def parse_construct(testapp, alldata, content_type, indices, uuid, value, docsdir):

    source = value.pop('source')
    try:
        value['source_uuid'] = indices['source'][source]
    except KeyError:
        raise ValueError('Unable to find source: %s' % source)


@parse_decorator_factory('biosample', {})
def parse_biosample(testapp, alldata, content_type, indices, uuid, value, docsdir):

    '''alias_list  alias_source_list  still not handled'''

    ''' MANDATORY FIELDS '''
    #value['organism_uuid'] = indices['organism'][value.pop('organism_no')]
    #if uuid == '6d26ea14-2548-459b-bdd7-e7afb954e7e8':
    #    import pdb;pdb.set_trace()
    source = value.pop('source')
    try:
        value['source_uuid'] = indices['source'][source]
    except KeyError:
        raise ValueError('Unable to find source: %s' % source)

    assign_submitter(value, content_type, indices,
                     {
                     'email': value.pop('submitted_by_colleague_email'),
                     'lab_name': value.pop('submitted_by_lab_name'),
                     'award_no': value.pop('submitted_by_award_number')
                     }
                     )

    donor = value.pop('donor')
    donor_uuid = indices['donor'][donor]
    if donor_uuid:
        try:
            d = alldata['donor'][donor_uuid]
            value['donor_uuid'] = donor_uuid
        except KeyError:
            raise ValueError('Unable to find donor for biosample: %s' % donor)

    ''' OPTIONAL OR REQUIRED FIELDS '''

    value['document_uuids'] = []

    try:
        documents = value.pop('document_list')

        for doc in documents:
            try:
                document_uuid = indices['document'].get(doc, None)
                if alldata['document'].get(document_uuid, None) is None:
                    raise ValueError('Missing/skipped document reference %s for biosample: %s' % (doc, uuid))
                else:
                    value['document_uuids'].append(document_uuid)
            except KeyError:
                raise ValueError('Unable to find document for biosample: %s' % doc)
    except KeyError:
        logger.warn('Empty biosample documents list: %s' % documents)

    value['treatment_uuids'] = []  # eventhough it's really 1:0 or 1.
    try:
        treat = value.pop('treatment')
        treatment_uuid = indices['treatment'][treat]
        try:
            if alldata['treatment'].get(treatment_uuid, None) is None:
                logger.warn('Missing/skipped treatment reference %s for biosample: %s' % (treatment_uuid, uuid))
            value['treatment_uuids'].append(treatment_uuid)
            # adding treatment documents to biosamples documents list
            if alldata['treatment'][treatment_uuid]['document_uuids']:
                value['document_uuids'] = value['document_uuids'] + alldata['treatment'][treatment_uuid]['document_uuids']
        except KeyError:
            raise ValueError('Unable to find treatment for biosample: %s' % treat)
    except KeyError as k:
        pass
        # treatment is often null

    value['construct_uuids'] = []
    try:
        constructs = value.pop('construct_list')

        for ctx in constructs:
            construct_uuid = indices['construct'].get(ctx, [])
            if alldata['construct'].get(construct_uuid, None) is None:
                logger.warn('Missing/skipped construct reference %s for biosample: %s' % (construct_uuid, uuid))
                ## but don't raise error
            else:
                value['construct_uuids'].append(construct_uuid)
    except:
        pass
        # protocol documents can be missing?

    value['related_biosample_uuid'] = ''
    value['related_biosample_accession'] = ''
    sample = value.pop('related_biosample_derived_from')
    if sample is not None:
        value['related_biosample_uuid'] = indices['biosample'][sample]
        value['related_biosample_accession'] = sample


@parse_decorator_factory('platform', {'value': '_uuid'})
def parse_platform(testapp, alldata, content_type, indices, uuid, value, docsdir):
    geo_ids = value.pop('geo_dbxref_list')
    value['gpl_ids'] = []
    gpl_ids = geo_ids.split(';')
    for gpl_id in gpl_ids:
        value['gpl_ids'].append(gpl_id.strip())


@parse_decorator_factory('library', {'value': '_uuid'})
def parse_library(testapp, alldata, content_type, indices, uuid, value, docsdir):

    ''' Biosample, documents and submitter are MANDATORY FIELDS for library '''

    value['biosample_uuid'] = ''
    try:
        biosample_accession = value.pop('biosample_accession')
        biosample_uuid = indices['biosample'][biosample_accession]
        try:
            if alldata['biosample'].get(biosample_uuid, None) is None:
                raise ValueError('Missing/skipped biosample reference')
            value['biosample_uuid'] = biosample_uuid
        except KeyError:
            raise ValueError('Unable to find biosample for library: %s' % biosample_accession)
    except KeyError:
        raise ValueError('Missing biosample for library: %s' % uuid)

    value['document_uuids'] = []
    try:
        documents = value.pop('document_list')

        for doc in documents:
            try:
                document_uuid = indices['document'].get(doc, [])
                if alldata['document'].get(document_uuid, None) is None:
                    raise ValueError('Missing/skipped document reference for library')
                else:
                    value['document_uuids'].append(document_uuid)
            except KeyError:
                raise ValueError('Unable to find document for library: %s' % doc)
    except:
        logger.warn('Document %s for library  %s are not found' % (documents, uuid))

    assign_submitter(value, content_type, indices,
                     {
                     'email': value.pop('submitted_by_colleague_email'),
                     'lab_name': value.pop('submitted_by_lab'),
                     'award_no': value.pop('submitted_by_award')
                     }
                     )


@parse_decorator_factory('assay', {'value': 'assay_name'})
def parse_assay(testapp, alldata, content_type, indices, uuid, value, docsdir):
    pass


@parse_decorator_factory('replicate', {'value': '_uuid'})
def parse_replicate(testapp, alldata, content_type, indices, uuid, value, docsdir):

    ''' MANDATORY FIELDS for a replicate '''

    # Checking for assay reference
    value['assay_uuid'] = ''
    try:
        assay_name = value.pop('assay_type')
        assay_uuid = indices['assay'][assay_name]
        try:
            if alldata['assay'].get(assay_uuid, None) is None:
                raise ValueError('Missing/skipped assay reference')
            value['assay_uuid'] = assay_uuid
        except KeyError:
            raise ValueError('Unable to find assay for replicate: %s' % assay_name)
    except KeyError:
        raise ValueError('Unable to find assay reference for replicate: %s' % uuid)

    # Checking for library reference
    if value['library_uuid'] is None:
        raise ValueError('Missing library UUID for replicate %s' % uuid)
    else:
        try:
            if alldata['library'].get(value['library_uuid'], None) is None:
                raise ValueError('Missing/skipped library reference')
        except KeyError:
            raise ValueError('Unable to find library reference for replicate')

    # Checking for platform reference
    if value['platform_uuid'] is None:
        raise ValueError('Missing platform UUID for replicate')
    else:
        try:
            if alldata['platform'].get(value['platform_uuid'], None) is None:
                raise ValueError('Missing/skipped platform reference')
        except KeyError:
            raise ValueError('Unable to find platform reference for replicate')


@parse_decorator_factory('file', {'value': '_uuid'})
def parse_file(testapp, alldata, content_type, indices, uuid, value, docsdir):

    ''' MANDATORY FIELDS for file '''

    # Check for replicate reference
    if value['replicate_uuid']:
        try:
            if alldata['replicate'].get(value['replicate_uuid'], None) is None:
                raise ValueError('Missing/skipped replicate reference')
            else:
                value['biological_replicate_number'] = \
                    alldata['replicate'][value['replicate_uuid']]['biological_replicate_number']
                value['technical_replicate_number'] = \
                    alldata['replicate'][value['replicate_uuid']]['technical_replicate_number']
        except KeyError:
            raise ValueError('Unable to find replicate for file')

    # Check for experiment reference
    try:
        if value['experiment_dataset_uuid'] not in indices['experiment']:
            raise ValueError('Missing/skipped experiment reference')
    except KeyError:
        raise ValueError('Unable to find experiment for file: %s' % uuid)

    # Chop long file names
    if value['file_name_encode3']:
        if(len(value['file_name_encode3']) > 60):
            value['temp_file_name'] = value['file_name_encode3'][:60] + "..."
        else:
            value['temp_file_name'] = value['file_name_encode3']

    assign_submitter(value, content_type, indices,
                     {
                     'email': value.pop('submitted_by_colleague_email'),
                     'lab_name': value.pop('submitted_by_lab'),
                     'award_no': value.pop('submitted_by_grant')
                     }
                     )


@parse_decorator_factory('experiment', {'value': '_uuid'})
def parse_experiment(testapp, alldata, content_type, indices, uuid, value, docsdir):

    ''' MANDATORY FIELDS for experiment '''

    value['file_uuids'] = []
    value['replicate_uuids'] = []
    value['experiment_control_uuids'] = []

    for file in alldata['file']:
        if (alldata['file'][file])['experiment_dataset_uuid'] is value['_uuid']:
            value['file_uuids'].append(file)
            for replicate in alldata['replicate']:
                if (alldata['file'][file])['replicate_uuid'] is replicate:
                    if replicate not in value['replicate_uuids']:
                        value['replicate_uuids'].append(replicate)
        else:
            pass

    # Handling controls here
    for file_uuid in value['file_uuids']:
        if alldata['file'][file_uuid]['possible_controls']:
            if not value['experiment_control_uuids']:
                value['experiment_control_uuids'].append(alldata['file'][file_uuid]['possible_controls'])

    #checking for replicates without files
    for replicate in alldata['replicate']:
        if alldata['replicate'][replicate]['experiment_accession'] is value['dataset_accession']:
            if replicate not in value['replicate_uuids']:
                value['replicate_uuids'].append(replicate)

    assign_submitter(value, content_type, indices,
                     {
                     'email': value.pop('submitted_by_colleague_email'),
                     'lab_name': value.pop('submitted_by_lab_name'),
                     'award_no': value.pop('submitted_by_award_number')
                     }
                     )


def load_all(testapp, filename, docsdir, test=False):
    sheets = [content_type for content_type in TYPE_URL]
    alldata = extract(filename, sheets, test=test)

    indices = IndexContainer().indices

    parse_award(testapp, alldata, indices, 'award', docsdir)

    parse_lab(testapp, alldata, indices, 'lab', docsdir)

    parse_colleague(testapp, alldata, indices, 'colleague', docsdir)

    parse_organism(testapp, alldata, indices, 'organism', docsdir)

    parse_source(testapp, alldata, indices, 'source', docsdir)

    parse_target(testapp, alldata, indices, 'target', docsdir)

    parse_antibody_lot(testapp, alldata, indices, 'antibody_lot', docsdir)

    parse_validation(testapp, alldata, indices, 'validation', docsdir)

    parse_antibody_approval(testapp, alldata, indices, 'antibody_approval', docsdir)

    parse_donor(testapp, alldata, indices, 'donor', docsdir)

    parse_document(testapp, alldata, indices, 'document', docsdir)
    # if theis replaces valdiation documents it might need to move up in the list

    parse_treatment(testapp, alldata, indices, 'treatment', docsdir)

    parse_construct(testapp, alldata, indices, 'construct', docsdir)

    indices['biosample'] = value_index(alldata['biosample'], 'accession')

    parse_biosample(testapp, alldata, indices, 'biosample', docsdir)

    parse_platform(testapp, alldata, indices, 'platform', docsdir)

    parse_library(testapp, alldata, indices, 'library', docsdir)

    parse_assay(testapp, alldata, indices, 'assay', docsdir)

    parse_replicate(testapp, alldata, indices, 'replicate', docsdir)

    indices['experiment'] = value_index(alldata['experiment'], '_uuid')

    parse_file(testapp, alldata, indices, 'file', docsdir)

    parse_experiment(testapp, alldata, indices, 'experiment', docsdir)
