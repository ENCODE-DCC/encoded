from base64 import b64decode
from cStringIO import StringIO
from mimetypes import guess_type
from PIL import Image
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from urllib2 import (
    quote,
    unquote,
)
from uuid import (
    UUID,
    uuid4,
)
from ..contentbase import Item
from ..storage import (
    Blob,
    DBSession,
)
from ..validation import ValidationFailure
import magic
import mimetypes


def parse_data_uri(uri):
    if not uri.startswith('data:'):
        raise ValueError(uri)
    meta, data = uri[len('data:'):].split(',', 1)
    meta = meta.split(';')
    mime_type = meta[0] or None
    charset = None
    is_base64 = False
    for part in meta[1:]:
        if part == 'base64':
            is_base64 = True
            continue
        if part.startswith('charset='):
            charset = part[len('charset='):]
            continue
        raise ValueError(uri)

    if is_base64:
        data = b64decode(data)
    else:
        data = unquote(data)

    return mime_type, charset, data


def mimetypes_are_equal(m1, m2):
    major1 = m1.split('/')[0]
    major2 = m2.split('/')[0]
    if major1 == 'text' and major2 == 'text':
        return True
    return m1 == m2


class ItemWithAttachment(Item):
    """ Item base class with attachment blob
    """
    download_property = 'attachment'

    @classmethod
    def _process_downloads(cls, parent, properties, sheets):
        prop_name = cls.download_property
        attachment = properties.get(prop_name, {})
        href = attachment.get('href', None)
        if href is not None:
            if not href.startswith('data:'):
                msg = "Expected data URI."
                raise ValidationFailure('body', [prop_name, 'href'], msg)

            properties = properties.copy()
            properties[prop_name] = attachment = attachment.copy()

            if sheets is None:
                sheets = {}
            else:
                sheets = sheets.copy()
            sheets['downloads'] = downloads = {}
            download_meta = downloads[prop_name] = {}

            try:
                mime_type_declared, charset, data = parse_data_uri(href)
            except (ValueError, TypeError):
                msg = 'Could not parse data URI.'
                raise ValidationFailure('body', [prop_name, 'href'], msg)
            if charset is not None:
                download_meta['charset'] = charset
            # Make sure the mimetype appears to be what the client says it is
            mime_type_detected = magic.from_buffer(data, mime=True)
            if mime_type_declared and not mimetypes_are_equal(mime_type_declared, mime_type_detected):
                msg = "Incorrect file type. (Appears to be %s)" % mime_type_detected
                raise ValidationFailure('body', [prop_name, 'href'], msg)
            mime_type = mime_type_declared or mime_type_detected
            attachment['type'] = mime_type
            if mime_type is not None:
                download_meta['type'] = mime_type

            # Make sure mimetype is not disallowed
            try:
                allowed_types = parent.schema['properties'][prop_name]['properties']['type']['enum']
            except KeyError:
                pass
            else:
                if mime_type not in allowed_types:
                    raise ValidationFailure(
                        'body', [prop_name, 'href'], 'Mimetype is not allowed.')

            # Make sure the file extensions matches the mimetype
            download_meta['download'] = filename = attachment['download']
            mime_type_from_filename, _ = mimetypes.guess_type(filename)
            if not mimetypes_are_equal(mime_type, mime_type_from_filename):
                raise ValidationFailure(
                    'body', [prop_name, 'href'], 'Wrong file extension for %s mimetype.' % mime_type)

            # Validate images and store height/width
            major, minor = mime_type.split('/')
            if major == 'image' and minor in ('png', 'jpeg', 'gif', 'tiff'):
                stream = StringIO(data)
                im = Image.open(stream)
                im.verify()
                attachment['width'], attachment['height'] = im.size

            blob_id = uuid4()
            download_meta['blob_id'] = str(blob_id)
            session = DBSession()
            blob = Blob(blob_id=blob_id, data=data)
            session.add(blob)
            attachment['href'] = '@@download/%s/%s' % (
                prop_name, quote(filename))

        return properties, sheets

    @classmethod
    def create(cls, parent, uuid, properties, sheets=None):
        properties, sheets = cls._process_downloads(parent, properties, sheets)
        item = super(ItemWithAttachment, cls).create(
            parent, uuid, properties, sheets)
        return item

    def update(self, properties, sheets=None):
        prop_name = self.download_property
        attachment = properties.get(prop_name, {})
        href = attachment.get('href', None)
        if href is not None:
            if href.startswith('@@download/'):
                try:
                    existing = self.properties[prop_name]['href']
                except KeyError:
                    existing = None
                if existing != href:
                    msg = "Expected data uri or existing uri."
                    raise ValidationFailure('body', [prop_name, 'href'], msg)
            else:
                properties, sheets = self._process_downloads(
                    self.__parent__, properties, sheets)

        super(ItemWithAttachment, self).update(properties, sheets)


@view_config(name='download', context=ItemWithAttachment, request_method='GET',
             permission='view', subpath_segments=2)
def download(context, request):
    prop_name, filename = request.subpath
    downloads = context.model['downloads']
    try:
        download_meta = downloads[prop_name]
    except KeyError:
        raise HTTPNotFound(prop_name)

    if download_meta['download'] != filename:
        raise HTTPNotFound(filename)

    blob_id = UUID(download_meta['blob_id'])

    mimetype, content_encoding = guess_type(filename, strict=False)
    if mimetype is None:
        mimetype = 'application/octet-stream'

    session = DBSession()
    blob = session.query(Blob).get(blob_id)

    headers = {
        'Content-Type': mimetype,
    }

    response = Response(body=blob.data, headers=headers)
    return response
