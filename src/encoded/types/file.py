from ..contentbase import (
    calculated_property,
    collection,
)
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
from pyramid.view import view_config
from urllib.parse import (
    parse_qs,
    urlparse,
)
import boto
import datetime
import json
import pytz
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


@collection(
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

    rev = {
        'paired_with': ('file', 'paired_with'),
    }

    embedded = [
        'replicate',
        'replicate.experiment',
        'replicate.experiment.lab',
        'replicate.experiment.target',
        'derived_from',
        'steps',
        'steps.analysis_step',
        'steps.analysis_step.software_versions',
        'steps.analysis_step.software_versions.software',
        'pipeline',
        'submitted_by',
    ]

    def unique_keys(self, properties):
        keys = super(File, self).unique_keys(properties)
        if properties.get('status') != 'replaced':
            if 'md5sum' in properties:
                value = 'md5:{md5sum}'.format(**properties)
                keys.setdefault('alias', []).append(value)
            # Ensure no files have multiple reverse paired_with
            if 'paired_with' in properties:
                keys.setdefault('file:paired_with', []).append(properties['paired_with'])
        return keys

    # Don't specify schema as this just overwrites the existing value
    @calculated_property(
        condition=lambda paired_end=None: paired_end == '1')
    def paired_with(self, root, request):
        paired_with = self.get_rev_links('paired_with')
        if not paired_with:
            return None
        item = root.get_by_uuid(paired_with[0])
        return request.resource_path(item)

    @calculated_property(schema={
        "title": "Download URL",
        "type": "string",
    })
    def href(self, request, accession, file_format):
        file_extension = self.schema['file_format_file_extension'][file_format]
        filename = '{}{}'.format(accession, file_extension)
        return request.resource_path(self, '@@download', filename)

    @calculated_property(condition=show_upload_credentials, schema={
        "type": "object",
    })
    def upload_credentials(self):
        return self.propsheets['external']['upload_credentials']

    @classmethod
    def create(cls, registry, properties, sheets=None):
        if properties.get('status') == 'uploading':
            sheets = {} if sheets is None else sheets.copy()

            bucket = registry.settings['file_upload_bucket']
            mapping = cls.schema['file_format_file_extension']
            file_extension = mapping[properties['file_format']]
            date = properties['date_created'].split('T')[0].replace('-', '/')
            key = '{date}/{uuid}/{accession}{file_extension}'.format(
                date=date, file_extension=file_extension, **properties)
            name = 'upload-{time}-{accession}'.format(
                time=time.time(), **properties)  # max 32 chars

            sheets['external'] = external_creds(bucket, key, name)
        return super(File, cls).create(registry, properties, sheets)


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
    mapping = context.schema['file_format_file_extension']
    file_extension = mapping[properties['file_format']]
    filename = properties['accession'] + file_extension
    if request.subpath:
        _filename, = request.subpath
        if filename != _filename:
            raise HTTPNotFound(_filename)

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
            'expires': datetime.datetime.fromtimestamp(expires, pytz.utc).isoformat(),
        }

    # 307 redirect specifies to keep original method
    raise HTTPTemporaryRedirect(location=location)
