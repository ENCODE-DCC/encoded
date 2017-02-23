from snovault import (
    AfterModified,
    BeforeModified,
    CONNECTION,
    calculated_property,
    collection,
    load_schema,
)
from snovault.schema_utils import schema_validator
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


def external_creds(bucket, key, name, profile_name=None):
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
    conn = boto.connect_sts(profile_name=profile_name)
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


def property_closure(request, propname, root_uuid):
    # Must avoid cycles
    conn = request.registry[CONNECTION]
    seen = set()
    remaining = {str(root_uuid)}
    while remaining:
        seen.update(remaining)
        next_remaining = set()
        for uuid in remaining:
            obj = conn.get_by_uuid(uuid)
            next_remaining.update(obj.__json__(request).get(propname, ()))
        remaining = next_remaining - seen
    return seen


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
        'paired_with': ('File', 'paired_with'),
        'quality_metrics': ('QualityMetric', 'quality_metric_of'),
        'superseded_by': ('File', 'supersedes'),
    }

    embedded = [
        'award',
        'award.pi',
        'award.pi.lab',
        'replicate',
        'replicate.experiment',
        'replicate.experiment.lab',
        'replicate.experiment.target',
        'replicate.library',
        'lab',
        'submitted_by',
        'analysis_step_version.analysis_step',
        'analysis_step_version.analysis_step.pipelines',
        'analysis_step_version.software_versions',
        'analysis_step_version.software_versions.software',
        'quality_metrics',
        'step_run',
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
        "title": "Upload Credentials",
        "type": "object",
    })
    def upload_credentials(self):
        external = self.propsheets.get('external', None)
        if external is not None:
            return external.get('upload_credentials', None)

    @calculated_property(schema={
        "title": "Read length units",
        "type": "string",
        "enum": [
            "nt"
        ]
    })
    def read_length_units(self, read_length=None, mapped_read_length=None):
        if read_length is not None or mapped_read_length is not None:
            return "nt"

    @calculated_property(schema={
        "title": "Biological replicates",
        "type": "array",
        "items": {
            "title": "Biological replicate number",
            "description": "The identifying number of each relevant biological replicate",
            "type": "integer",
        }
    })
    def biological_replicates(self, request, registry, root, replicate=None):
        if replicate is not None:
            replicate_obj = traverse(root, replicate)['context']
            replicate_biorep = replicate_obj.__json__(request)['biological_replicate_number']
            return [replicate_biorep]

        conn = registry[CONNECTION]
        derived_from_closure = property_closure(request, 'derived_from', self.uuid)
        dataset_uuid = self.__json__(request)['dataset']
        obj_props = (conn.get_by_uuid(uuid).__json__(request) for uuid in derived_from_closure)
        replicates = {
            props['replicate']
            for props in obj_props
            if props['dataset'] == dataset_uuid and 'replicate' in props
        }
        bioreps = {
            conn.get_by_uuid(uuid).__json__(request)['biological_replicate_number']
            for uuid in replicates
        }
        return sorted(bioreps)

    @calculated_property(schema={
        "title": "Technical replicates",
        "type": "array",
        "items": {
            "title": "Technical replicate number",
            "description": "The identifying number of each relevant technical replicate",
            "type": "string"
        }
    })
    def technical_replicates(self, request, registry, root, replicate=None):
        if replicate is not None:
            replicate_obj = traverse(root, replicate)['context']
            replicate_biorep = replicate_obj.__json__(request)['biological_replicate_number']
            replicate_techrep = replicate_obj.__json__(request)['technical_replicate_number']
            tech_rep_string = str(replicate_biorep)+"_"+str(replicate_techrep)
            return [tech_rep_string]

        conn = registry[CONNECTION]
        derived_from_closure = property_closure(request, 'derived_from', self.uuid)
        dataset_uuid = self.__json__(request)['dataset']
        obj_props = (conn.get_by_uuid(uuid).__json__(request) for uuid in derived_from_closure)
        replicates = {
            props['replicate']
            for props in obj_props
            if props['dataset'] == dataset_uuid and 'replicate' in props
        }
        techreps = {
            str(conn.get_by_uuid(uuid).__json__(request)['biological_replicate_number']) +
            '_' + str(conn.get_by_uuid(uuid).__json__(request)['technical_replicate_number'])
            for uuid in replicates
        }
        return sorted(techreps)

    @calculated_property(schema={
        "title": "Analysis Step Version",
        "type": "string",
        "linkTo": "AnalysisStepVersion"
    })
    def analysis_step_version(self, request, root, step_run=None):
        if step_run is None:
            return
        step_run_obj = traverse(root, step_run)['context']
        step_version_uuid = step_run_obj.__json__(request).get('analysis_step_version')
        if step_version_uuid is not None:
            return request.resource_path(root[step_version_uuid])

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
            "linkFrom": "QualityMetric.quality_metric_of",
        },
    })
    def quality_metrics(self, request, quality_metrics):
        return paths_filtered_by_status(request, quality_metrics)

    @calculated_property(schema={
        "title": "File type",
        "type": "string"
    })
    def file_type(self, file_format, file_format_type=None):
        if file_format_type is None:
            return file_format
        else:
            return file_format + ' ' + file_format_type

    @calculated_property(schema={
        "title": "Superseded by",
        "description": "The file(s) that supersede this file (i.e. are more preferable to use).",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "File.supersedes",
        },
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

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

            profile_name = registry.settings.get('file_upload_profile_name')
            sheets['external'] = external_creds(bucket, key, name, profile_name)
        return super(File, cls).create(registry, uuid, properties, sheets)


@view_config(name='upload', context=File, request_method='GET',
             permission='edit')
def get_upload(context, request):
    external = context.propsheets.get('external', {})
    upload_credentials = external.get('upload_credentials')
    # Show s3 location info for files originally submitted to EDW.
    if upload_credentials is None and external.get('service') == 's3':
        upload_credentials = {
            'upload_url': 's3://{bucket}/{key}'.format(**external),
        }
    return {
        '@graph': [{
            '@id': request.resource_path(context),
            'upload_credentials': upload_credentials,
        }],
    }


@view_config(name='upload', context=File, request_method='POST',
             permission='edit', validators=[schema_validator({"type": "object"})])
def post_upload(context, request):
    properties = context.upgrade_properties()
    if properties['status'] not in ('uploading', 'upload failed'):
        raise HTTPForbidden('status must be "uploading" to issue new credentials')

    accession_or_external = properties.get('accession') or properties['external_accession']
    external = context.propsheets.get('external', None)

    if external is None:
        # Handle objects initially posted as another state.
        bucket = request.registry.settings['file_upload_bucket']
        uuid = context.uuid
        mapping = context.schema['file_format_file_extension']
        file_extension = mapping[properties['file_format']]
        date = properties['date_created'].split('T')[0].replace('-', '/')
        key = '{date}/{uuid}/{accession_or_external}{file_extension}'.format(
            accession_or_external=accession_or_external,
            date=date, file_extension=file_extension, uuid=uuid, **properties)
    elif external.get('service') == 's3':
        bucket = external['bucket']
        key = external['key']
    else:
        raise ValueError(external.get('service'))

    name = 'up{time:.6f}-{accession_or_external}'.format(
        accession_or_external=accession_or_external,
        time=time.time(), **properties)[:32]  # max 32 chars
    profile_name = request.registry.settings.get('file_upload_profile_name')
    creds = external_creds(bucket, key, name, profile_name)

    new_properties = None
    if properties['status'] == 'upload failed':
        new_properties = properties.copy()
        new_properties['status'] = 'uploading'

    registry = request.registry
    registry.notify(BeforeModified(context, request))
    context.update(new_properties, {'external': creds})
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

    use_download_proxy = request.client_addr not in request.registry['aws_ipset']

    external = context.propsheets.get('external', {})
    if external.get('service') == 's3':
        conn = boto.connect_s3()
        location = conn.generate_url(
            36*60*60, request.method, external['bucket'], external['key'],
            force_http=proxy or use_download_proxy, response_headers={
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

    # We don't use X-Accel-Redirect here so that client behaviour is similar for
    # both aws and non-aws users.
    if use_download_proxy:
        location = request.registry.settings.get('download_proxy', '') + str(location)

    # 307 redirect specifies to keep original method
    raise HTTPTemporaryRedirect(location=location)
