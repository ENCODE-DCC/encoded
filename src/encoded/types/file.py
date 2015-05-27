from contentbase import (
    AfterModified,
    BeforeModified,
    calculated_property,
    collection,
)
from contentbase.schema_utils import (
    load_schema,
    schema_validator,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPTemporaryRedirect,
    HTTPNotFound,
)
from pyramid.response import Response
from pyramid.settings import asbool
from pyramid.traversal import traverse
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
    schema = load_schema('encoded:schemas/file.json')
    name_key = 'accession'

    rev = {
        'paired_with': ('file', 'paired_with'),
        'qc_metrics': ('quality_metric', 'files'),
    }

    embedded = [
        'replicate',
        'replicate.experiment',
        'replicate.experiment.lab',
        'replicate.experiment.target',
        'lab',
        'derived_from',
        'submitted_by',
        'pipeline',
        'analysis_step',
        'analysis_step.software_versions',
        'analysis_step.software_versions.software',
        'qc_metrics.step_run.analysis_step',
    ]

    @property
    def __name__(self):
        properties = self.upgrade_properties()
        if 'external_accession' in properties:
            return properties['external_accession']
        if properties.get('status') == 'replaced':
            return self.uuid
        return properties.get(self.name_key, None) or self.uuid

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

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, accession=None, external_accession=None):
        return accession or external_accession

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
    def href(self, request, file_format, accession=None, external_accession=None):
        accession = accession or external_accession
        file_extension = self.schema['file_format_file_extension'][file_format]
        filename = '{}{}'.format(accession, file_extension)
        return request.resource_path(self, '@@download', filename)

    @calculated_property(condition=show_upload_credentials, schema={
        "type": "object",
    })
    def upload_credentials(self):
        return self.propsheets['external']['upload_credentials']

    @calculated_property(schema={
        "title": "Read length units",
        "type": "string",
        "enum": [
            "nt"
        ]
    })
    def read_length_units(self, read_length=None):
        if read_length is not None:
            return "nt"

    @calculated_property(schema={
        "title": "Pipeline",
        "type": "string",
        "linkTo": "pipeline"
    })
    def pipeline(self, root, request, step_run=None):
        if step_run is None:
            return
        workflow_uuid = traverse(root, step_run)['context'].__json__(request).get('workflow_run')
        if workflow_uuid is None:
            return
        pipeline_uuid = root[workflow_uuid].__json__(request).get('pipeline')
        if pipeline_uuid is None:
            return
        return request.resource_path(root[pipeline_uuid])

    @calculated_property(schema={
        "title": "Analysis Step",
        "type": "string",
        "linkTo": "analysis_step"
    })
    def analysis_step(self, request, step_run=None):
        if step_run is not None:
            return request.embed(step_run, '@@object').get('analysis_step')

    @calculated_property(schema={
        "title": "Output category",
        "type": "string",
        "enum": [
            "raw data",
            "alignment",
            "signal",
            "annotation",
            "quantification",
            "reference"
        ]
    })
    def output_category(self, output_type):
        return self.schema['output_type_output_category'].get(output_type)

    @calculated_property(schema={
        "title": "QC Metric",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "quality_metric.analysis_step_run",
        },
    })
    def qc_metrics(self, request, qc_metrics):
        return paths_filtered_by_status(request, qc_metrics)

    @calculated_property(schema={
        "title": "File type",
        "type": "string"
    })
    def file_type(self, file_format, file_format_type=None):
        if file_format_type is None:
            return file_format
        else:
            return file_format + ' ' + file_format_type

    @classmethod
    def create(cls, registry, uuid, properties, sheets=None):
        if properties.get('status') == 'uploading':
            sheets = {} if sheets is None else sheets.copy()

            bucket = registry.settings['file_upload_bucket']
            mapping = cls.schema['file_format_file_extension']
            file_extension = mapping[properties['file_format']]
            date = properties['date_created'].split('T')[0].replace('-', '/')
            accession_or_external = properties.get('accession') or properties['external_accession']
            key = '{date}/{uuid}/{accession_or_external}{file_extension}'.format(
                accession_or_external=accession_or_external,
                date=date, file_extension=file_extension, uuid=uuid, **properties)
            name = 'up{time:.6f}-{accession_or_external}'.format(
                accession_or_external=accession_or_external,
                time=time.time(), **properties)[:32]  # max 32 chars

            sheets['external'] = external_creds(bucket, key, name)
        return super(File, cls).create(registry, uuid, properties, sheets)


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
    properties = context.upgrade_properties()
    if properties['status'] not in ('uploading', 'upload failed'):
        raise HTTPForbidden('status must be "uploading" to issue new credentials')

    external = context.propsheets.get('external', {})
    if external.get('service') != 's3':
        raise ValueError(external.get('service'))

    bucket = external['bucket']
    key = external['key']
    accession_or_external = properties.get('accession') or properties['external_accession']
    name = 'up{time:.6f}-{accession_or_external}'.format(
        accession_or_external=accession_or_external,
        time=time.time(), **properties)  # max 32 chars
    creds = external_creds(bucket, key, name)

    registry = request.registry
    registry.notify(BeforeModified(context, request))
    context.update(None, {'external': creds})
    registry.notify(AfterModified(context, request))

    rendered = request.embed('/%s/@@object' % context.uuid, as_user=True)
    result = {
        'status': 'success',
        '@type': ['result'],
        '@graph': [rendered],
    }
    return result


@view_config(name='download', context=File, request_method='GET',
             permission='view', subpath_segments=[0, 1])
def download(context, request):
    properties = context.upgrade_properties()
    mapping = context.schema['file_format_file_extension']
    file_extension = mapping[properties['file_format']]
    accession_or_external = properties.get('accession') or properties['external_accession']
    filename = accession_or_external + file_extension
    if request.subpath:
        _filename, = request.subpath
        if filename != _filename:
            raise HTTPNotFound(_filename)

    proxy = asbool(request.params.get('proxy')) or 'Origin' in request.headers

    external = context.propsheets.get('external', {})
    if external.get('service') == 's3':
        conn = boto.connect_s3()
        location = conn.generate_url(
            36*60*60, request.method, external['bucket'], external['key'],
            force_http=proxy, response_headers={
                'response-content-disposition': "attachment; filename=" + filename,
            })
    else:
        raise ValueError(external.get('service'))

    if asbool(request.params.get('soft')):
        expires = int(parse_qs(urlparse(location).query)['Expires'][0])
        return {
            '@type': ['SoftRedirect'],
            'location': location,
            'expires': datetime.datetime.fromtimestamp(expires, pytz.utc).isoformat(),
        }

    if proxy:
        return Response(headers={'X-Accel-Redirect': '/_proxy/' + str(location)})

    # 307 redirect specifies to keep original method
    raise HTTPTemporaryRedirect(location=location)
