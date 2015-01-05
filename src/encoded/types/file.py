from ..contentbase import location
from ..embedding import embed
from ..schema_utils import (
    load_schema,
    schema_validator,
)
from .base import (
    Item,
)
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPTemporaryRedirect,
    HTTPNotFound,
)
from pyramid.response import Response
from pyramid.settings import asbool
from pyramid.traversal import find_root
from pyramid.view import view_config
from urllib.parse import (
    parse_qs,
    urlparse,
)
import boto
import datetime
import json
import time


def show_upload_credentials(request=None, context=None, status=None):
    if request is None or status not in ('uploading', 'upload failed'):
        return False
    return request.has_permission('edit', context)


def external_creds(bucket, key, name):
    policy = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Effect': 'Allow',
                'Action': 's3:PutObject',
                'Resource': 'arn:aws:s3:::{bucket}/{key}'.format(bucket=bucket, key=key),
            }
        ]
    }
    conn = boto.connect_sts(profile_name='encoded-files-upload')
    token = conn.get_federation_token(name, policy=json.dumps(policy))
    # 'access_key' 'secret_key' 'expiration' 'session_token'
    credentials = token.credentials.to_dict()
    credentials.update({
        'upload_url': 's3://{bucket}/{key}'.format(bucket=bucket, key=key),
        'federated_user_arn': token.federated_user_arn,
        'federated_user_id': token.federated_user_id,
        'request_id': token.request_id,
    })
    return {
        'service': 's3',
        'bucket': bucket,
        'key': key,
        'upload_credentials': credentials,
    }


@location(
    name='files',
    unique_key='accession',
    properties={
        'title': 'Files',
        'description': 'Listing of Files',
    })
class File(Item):
    item_type = 'file'
    schema = load_schema('file.json')
    name_key = 'accession'
    template_keys = [
        {
            'name': 'alias',
            'value': 'md5:{md5sum}',
            '$templated': True,
            '$condition': lambda md5sum=None, status=None: md5sum and status != 'replaced',
        },
    ]
    template = {
        'href': {
            '$value': '{item_uri}@@download/{accession}{file_extension}',
            '$templated': True,
        },
        'upload_credentials': {
            '$templated': True,
            '$condition': show_upload_credentials,
            '$value': lambda context: context.propsheets['external']['upload_credentials'],
        }
    }

    def template_namespace(self, properties, request=None):
        ns = super(File, self).template_namespace(properties, request)
        mapping = self.schema['file_format_file_extension']
        ns['file_extension'] = mapping[properties['file_format']]
        return ns

    @classmethod
    def create(cls, parent, properties, sheets=None):
        if properties.get('status') == 'uploading':
            sheets = {} if sheets is None else sheets.copy()

            registry = find_root(parent).registry
            bucket = registry.settings['file_upload_bucket']
            mapping = cls.schema['file_format_file_extension']
            file_extension = mapping[properties['file_format']]
            date = properties['date_created'].split('T')[0].replace('-', '/')
            key = '{date}/{uuid}/{accession}{file_extension}'.format(
                date=date, file_extension=file_extension, **properties)
            name = 'upload-{time}-{accession}'.format(
                time=time.time(), **properties)  # max 32 chars

            sheets['external'] = external_creds(bucket, key, name)
        return super(File, cls).create(parent, properties, sheets)


@view_config(name='upload', context=File, request_method='GET',
             permission='edit')
def get_upload(context, request):
    external = context.propsheets.get('external', {})
    if external.get('service') != 's3':
        raise ValueError(external.get('service'))
    return {
        '@graph': [{
            '@id': request.resource_path(context),
            'upload_credentials': external['upload_credentials'],
        }],
    }


@view_config(name='upload', context=File, request_method='POST',
             permission='edit', validators=[schema_validator({"type": "object"})])
def post_upload(context, request):
    properties = context.upgrade_properties(finalize=False)
    if properties['status'] not in ('uploading', 'upload failed'):
        raise HTTPForbidden('status must be "uploading" to issue new credentials')

    external = context.propsheets.get('external', {})
    if external.get('service') != 's3':
        raise ValueError(external.get('service'))

    bucket = external['bucket']
    key = external['key']
    name = 'upload-{time}-{accession}'.format(
        time=time.time(), **properties)  # max 32 chars
    creds = external_creds(bucket, key, name)
    context.update(None, {'external': creds})
    rendered = embed(request, '/%s/@@object' % context.uuid, as_user=True)
    result = {
        'status': 'success',
        '@type': ['result'],
        '@graph': [rendered],
    }
    return result


class InternalResponse(Response):
    def _abs_headerlist(self, environ):
        """Avoid making the Location header absolute.
        """
        return list(self.headerlist)


@view_config(name='download', context=File, request_method='GET',
             permission='view', subpath_segments=[0, 1])
def download(context, request):
    properties = context.upgrade_properties(finalize=False)
    ns = context.template_namespace(properties, request)
    if request.subpath:
        filename, = request.subpath
        if filename != '{accession}{file_extension}'.format(**ns):
            raise HTTPNotFound(filename)
    else:
        filename = '{accession}{file_extension}'.format(**ns)

    proxy = asbool(request.params.get('proxy'))

    external = context.propsheets.get('external', {})
    if external.get('service') == 's3':
        conn = boto.connect_s3()
        method = 'GET' if proxy else request.method  # mod_wsgi forces a GET
        location = conn.generate_url(
            36*60*60, method, external['bucket'], external['key'],
            response_headers={
                'response-content-disposition': "attachment; filename=" + filename,
            })
    else:
        raise ValueError(external.get('service'))

    if proxy:
        return InternalResponse(location='/_proxy/' + location)

    if asbool(request.params.get('soft')):
        expires = int(parse_qs(urlparse(location).query)['Expires'][0])
        return {
            '@type': ['SoftRedirect'],
            'location': location,
            'expires': datetime.datetime.fromtimestamp(expires).isoformat(),
        }

    # 307 redirect specifies to keep original method
    raise HTTPTemporaryRedirect(location=location)
