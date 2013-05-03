from base64 import b64decode
from mimetypes import guess_type
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


class ItemWithDocument(Item):
    """ Item base class with document blob
    """
    @classmethod
    def create(cls, parent, uuid, properties):
        additional_sheets = {}
        if properties['document']['href'].startswith('data:'):
            properties = properties.copy()
            properties['document'] = document = properties['document'].copy()

            download_meta = {}
            download_meta['download'] = filename = document['download']
            mime_type, charset, data = parse_data_uri(document['href'])
            if mime_type is not None:
                download_meta['type'] = mime_type
            if charset is not None:
                download_meta['charset'] = charset
            blob_id = uuid4()
            session = DBSession()
            blob = Blob(blob_id=blob_id, data=data)
            session.add(blob)
            additional_sheets['downloads'] = {str(blob_id): download_meta}
            document['href'] = '@@download/%s/%s' % (blob_id, quote(filename))

        item = super(ItemWithDocument, cls).create(
            parent, uuid, properties, **additional_sheets)
        return item


@view_config(name='download', context=ItemWithDocument, request_method='GET',
             permission='view', subpath_segments=2)
def download(context, request):
    blob_id, filename = request.subpath
    downloads = context.model.resource['downloads']
    try:
        blob_id = UUID(blob_id)
    except ValueError:
        raise HTTPNotFound(blob_id)

    try:
        download = downloads[str(blob_id)]
    except KeyError:
        raise HTTPNotFound(blob_id)

    if download['download'] != filename:
        raise HTTPNotFound(filename)

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
