from botocore.exceptions import ClientError
from botocore.config import Config
from snovault import (
    AfterModified,
    BeforeModified,
    CONNECTION,
    calculated_property,
    collection,
    load_schema,
)
from snovault.attachment import InternalRedirect
from snovault.schema_utils import schema_validator
from snovault.util import Path
from snovault.validation import ValidationFailure
from .base import (
    Item,
    paths_filtered_by_status
)
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPTemporaryRedirect,
    HTTPNotFound,
)
from pyramid.settings import asbool
from pyramid.traversal import traverse
from pyramid.view import view_config
from urllib.parse import (
    parse_qs,
    urlparse,
)
import base64
import boto3
import botocore
import datetime
import logging
import json
import pytz
import time

from encoded.upload_credentials import UploadCredentials
from snovault.util import ensure_list_and_filter_none
from snovault.util import take_one_or_return_none
from snovault.util import try_to_get_field_from_item_with_skip_calculated_first


def show_upload_credentials(request=None, context=None, status=None):
    if request is None or status not in ('uploading', 'upload failed'):
        return False
    return request.has_permission('edit', context)


def show_cloud_metadata(status=None, md5sum=None, file_size=None, restricted=None, no_file_available=None):
    if restricted or not md5sum or not file_size or no_file_available:
        return False
    return True


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


ENCODE_PROCESSING_PIPELINE_UUID = 'a558111b-4c50-4b2e-9de8-73fd8fd3a67d'
RAW_OUTPUT_TYPES = ['reads', 'rejected reads', 'raw data', 'reporter code counts', 'intensity values', 'idat red channel', 'idat green channel']


def file_is_md5sum_constrained(properties):
    conditions = [
        properties.get('lab') != ENCODE_PROCESSING_PIPELINE_UUID,
        properties.get('output_type') in RAW_OUTPUT_TYPES
    ]
    return any(conditions)


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
        'analyses': ('Analysis', 'files'),
        'paired_with': ('File', 'paired_with'),
        'quality_metrics': ('QualityMetric', 'quality_metric_of'),
        'superseded_by': ('File', 'supersedes'),
    }

    embedded = [
        'platform',
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
    embedded_with_frame = [
        Path(
            'analyses',
            include=[
                '@id',
                '@type',
                'uuid',
                'status',
                'pipeline_award_rfas',
                'pipeline_version',
                'title',
            ],
        ),
        Path(
            'dataset_details',
            include=[
                '@id',
                '@type',
                'uuid',
                'status',
                'assay_title',
                'assay_term_name',
                'annotation_type',
                'biosample_ontology',
                'target',
                'targets',
            ],
        ),
        Path('dataset_details.biosample_ontology'),
        Path('dataset_details.target'),
        Path('dataset_details.targets'),
    ]
    audit_inherit = [
        'replicate',
        'replicate.experiment',
        'replicate.experiment.target',
        'replicate.library',
        'lab',
        'submitted_by',
        'analysis_step_version.analysis_step',
        'analysis_step_version.analysis_step.pipelines',
        'analysis_step_version.analysis_step.versions',
        'analysis_step_version.software_versions',
        'analysis_step_version.software_versions.software'
    ]
    set_status_up = [
        'quality_metrics',
        'platform',
        'step_run',
    ]
    set_status_down = []
    public_s3_statuses = ['released', 'archived']
    private_s3_statuses = ['in progress', 'replaced', 'deleted', 'revoked']

    audit = {
        'audit.ERROR.category': {
            'group_by': 'audit.ERROR.category',
            'label': 'Error'
        },
        'audit.INTERNAL_ACTION.category': {
            'group_by': 'audit.INTERNAL_ACTION.category',
            'label': 'Internal Action'},
        'audit.NOT_COMPLIANT.category': {
            'group_by': 'audit.NOT_COMPLIANT.category',
            'label': 'Not Compliant'
        },
        'audit.WARNING.category': {
            'group_by': 'audit.WARNING.category',
            'label': 'Warning'
        },
        'x': {
            'group_by': 'file_format', 'label': 'File format'
        }
    }

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
                resource = self.registry[CONNECTION].get_by_unique_key('alias', value)
                if resource and resource.uuid != self.uuid:
                    if file_is_md5sum_constrained(properties):
                        keys.setdefault('alias', []).append(value)
                else:
                    keys.setdefault('alias', []).append(value)
            # Ensure no files have multiple reverse paired_with
            if 'paired_with' in properties:
                keys.setdefault('file:paired_with', []).append(properties['paired_with'])
            if 'external_accession' in properties:
                keys.setdefault('external_accession', []).append(
                    properties['external_accession'])
        return keys

    @calculated_property(schema={
        "title": "Title",
        "description": "The title of the file either the accession or the external_accession.",
        "comment": "Do not submit. This is a calculated property",
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
        "description": "The download path for S3 to obtain the actual file.",
        "comment": "Do not submit. This is issued by the server.",
        "type": "string",
    })
    def href(self, request, file_format, accession=None, external_accession=None):
        accession = accession or external_accession
        file_extension = self.schema['file_format_file_extension'][file_format]
        filename = '{}{}'.format(accession, file_extension)
        return request.resource_path(self, '@@download', filename)

    @calculated_property(condition=show_upload_credentials, schema={
        "title": "Upload Credentials",
        "description": "The upload credentials for S3 to submit the file content.",
        "comment": "Do not submit. This is issued by the server.",
        "type": "object",
    })
    def upload_credentials(self):
        external = self.propsheets.get('external', None)
        if external is not None:
            return external.get('upload_credentials', None)

    @calculated_property(schema={
        "title": "Read length units",
        "description": "The units for read length.",
        "comment": "Do not submit. This is a fixed value.",
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
        "description": "The biological replicate numbers associated with this file.",
        "comment": "Do not submit.  This field is calculated through the derived_from relationship back to the raw data.",
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
        "description": "The technical replicate numbers associated with this file.",
        "comment": "Do not submit.  This field is calculated through the derived_from relationship back to the raw data.",
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
        "description": "The step version of the pipeline from which this file is an output.",
        "comment": "Do not submit.  This field is calculated from step_run.",
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
        "description": "The overall catagory of the file content.",
        "comment": "Do not submit.  This field is calculated from output_type_output_category.",
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
        "description": "The list of QC metric objects associated with this file.",
        "comment": "Do not submit. Values in the list are reverse links of a quality metric with this file in quality_metric_of field.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "QualityMetric.quality_metric_of",
        },
        "notSubmittable": True,
    })
    def quality_metrics(self, request, quality_metrics):
        return paths_filtered_by_status(request, quality_metrics)

    @calculated_property(schema={
        "title": "File type",
        "description": "The concatenation of file_format and file_format_type",
        "comment": "Do not submit. This field is calculated from file_format and file_format_type.",
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
        "comment": "Do not submit. Values in the list are reverse links of a file that supersedes.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "File.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(
        condition=show_cloud_metadata,
        schema={
            "title": "Cloud metadata",
            "description": "Metadata required for cloud transfer.",
            "comment": "Do not submit. Values are calculated from file metadata.",
            "type": "object",
            "notSubmittable": True,
        }
    )
    def cloud_metadata(self, md5sum, file_size):
        try:
            external = self._get_external_sheet()
        except HTTPNotFound:
            return None
        conn = boto3.client('s3', config=Config(
            signature_version=botocore.UNSIGNED,
        ))
        location = conn.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': external['bucket'],
                'Key': external['key']
            },
            ExpiresIn=0
        )
        return {
            'url': location,
            'md5sum_base64': base64.b64encode(bytes.fromhex(md5sum)).decode("utf-8"),
            'file_size': file_size
        }

    @calculated_property(
        condition=show_cloud_metadata,
        schema={
            "title": "S3 URI",
            "description": "The S3 URI of public file object.",
            "comment": "Do not submit. Value is calculated from file metadata.",
            "type": "string",
            "notSubmittable": True,
        }
    )
    def s3_uri(self):
        try:
            external = self._get_external_sheet()
        except HTTPNotFound:
            return None
        return 's3://{bucket}/{key}'.format(**external)

    @calculated_property(schema={
        "title": "Analyses",
        "description": "The analyses which the file belongs to.",
        "comment": "Do not submit. Values in the list are reverse links of Analysis with this file in files field.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Analysis.files",
        },
        "notSubmittable": True,
    })
    def analyses(self, request, analyses):
        return paths_filtered_by_status(request, analyses)

    @calculated_property(
        condition='dataset',
        define=True,
        schema={
            "title": "Dataset details",
            "description": "Place to store details embedded from dataset.",
            "comment": "Do not submit.",
            "type": "string",
            "linkTo": "Dataset",
            "notSubmittable": True,
        }
    )
    def dataset_details(self, dataset):
        return dataset

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
            upload_creds = UploadCredentials(bucket, key, name, profile_name=profile_name)
            s3_transfer_allow = registry.settings.get('external_aws_s3_transfer_allow', 'false')
            sheets['external'] = upload_creds.external_creds(
                s3_transfer_allow=asbool(s3_transfer_allow),
                s3_transfer_buckets=registry.settings.get('external_aws_s3_transfer_buckets'),
            )
        return super(File, cls).create(registry, uuid, properties, sheets)

    def _get_external_sheet(self):
        external = self.propsheets.get('external', {})
        if external.get('service') == 's3':
            return external
        else:
            raise HTTPNotFound()

    def _set_external_sheet(self, new_external):
        # This just updates external sheet, doesn't overwrite.
        external = self._get_external_sheet()
        external = external.copy()
        external.update(new_external)
        properties = self.upgrade_properties()
        self.update(properties, {'external': external})

    def set_public_s3(self):
        external = self._get_external_sheet()
        boto3.resource('s3').ObjectAcl(
            external['bucket'],
            external['key']
        ).put(ACL='public-read')

    def set_private_s3(self):
        external = self._get_external_sheet()
        boto3.resource('s3').ObjectAcl(
            external['bucket'],
            external['key']
        ).put(ACL='private')

    def _should_set_object_acl(self):
        '''
        Skip setting ACL on certain objects.
        '''
        properties = self.upgrade_properties()
        skip_acl_prop_keys = [
            'restricted',
            'no_file_available',
        ]
        if any(properties.get(prop_key) for prop_key in set(skip_acl_prop_keys)):
            return False
        return True

    def set_status(self, new_status, request, parent=True):
        status_set = super(File, self).set_status(
            new_status,
            request,
            parent=parent,
        )
        if not status_set or not asbool(request.params.get('update')):
            return False
        if self._should_set_object_acl():
            # Change permission in S3.
            try:
                if new_status in self.public_s3_statuses:
                    self.set_public_s3()
                elif new_status in self.private_s3_statuses:
                    self.set_private_s3()
            except ClientError as e:
                # Demo trying to set ACL on production object?
                if e.response['Error']['Code'] == 'AccessDenied':
                    logging.warn(e)
                else:
                    raise e
        return True

    def _file_in_correct_bucket(self, request):
        '''
        Returns : boolean, current_path, destination_path
        '''
        return_flag = True
        try:
            external = self._get_external_sheet()
        except HTTPNotFound:
            # File object doesn't exist, leave it alone.
            return (return_flag, None, None)
        # Restricted and no_file_available files should not be moved.
        if not self._should_set_object_acl():
            return (return_flag, None, None)
        public_bucket = request.registry.settings.get('pds_public_bucket')
        private_bucket = request.registry.settings.get('pds_private_bucket')
        properties = self.upgrade_properties()
        current_bucket = external.get('bucket')
        current_key = external.get('key')
        base_uri = 's3://{}/{}'
        current_path = base_uri.format(current_bucket, current_key)
        file_status = properties.get('status')
        if file_status in self.private_s3_statuses:
            if current_bucket != private_bucket:
                return_flag = False
            return (return_flag, current_path, base_uri.format(private_bucket, current_key))
        if file_status in self.public_s3_statuses:
            if current_bucket != public_bucket:
                return_flag = False
            return (return_flag, current_path, base_uri.format(public_bucket, current_key))
        # Assume correct bucket for unaccounted file statuses.
        return (return_flag, current_path, base_uri.format(private_bucket, current_key))


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
    file_upload_bucket = request.registry.settings['file_upload_bucket']
    external = context.propsheets.get('external', None)
    registry = request.registry
    if external is None:
        # Handle objects initially posted as another state.
        bucket = file_upload_bucket
        uuid = context.uuid
        mapping = context.schema['file_format_file_extension']
        file_extension = mapping[properties['file_format']]
        date = properties['date_created'].split('T')[0].replace('-', '/')
        key = '{date}/{uuid}/{accession_or_external}{file_extension}'.format(
            accession_or_external=accession_or_external,
            date=date, file_extension=file_extension, uuid=uuid, **properties)
    elif external.get('service') == 's3':
        bucket = external['bucket']
        # Must reset file to point to file_upload_bucket (keep AWS public dataset in sync).
        if bucket != file_upload_bucket:
            registry.notify(BeforeModified(context, request))
            context._set_external_sheet({'bucket': file_upload_bucket})
            registry.notify(AfterModified(context, request))
            bucket = file_upload_bucket
        key = external['key']
    else:
        raise HTTPNotFound(
            detail='External service {} not expected'.format(external.get('service'))
        )

    name = 'up{time:.6f}-{accession_or_external}'.format(
        accession_or_external=accession_or_external,
        time=time.time(), **properties)[:32]  # max 32 chars
    profile_name = request.registry.settings.get('file_upload_profile_name')
    upload_creds = UploadCredentials(bucket, key, name, profile_name=profile_name)
    s3_transfer_allow = request.registry.settings.get('external_aws_s3_transfer_allow', 'false')
    creds = upload_creds.external_creds(
        s3_transfer_allow=asbool(s3_transfer_allow),
        s3_transfer_buckets=request.registry.settings.get('external_aws_s3_transfer_buckets'),
    )
    new_properties = None
    if properties['status'] == 'upload failed':
        new_properties = properties.copy()
        new_properties['status'] = 'uploading'

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
    external = context.propsheets.get('external', {})
    if external.get('service') == 's3':
        conn = boto3.client('s3')
        location = conn.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': external['bucket'],
                'Key': external['key'],
                'ResponseContentDisposition': 'attachment; filename=' + filename
            },
            ExpiresIn=36*60*60
        )
    else:
        raise HTTPNotFound(
            detail='External service {} not expected'.format(external.get('service'))
        )
    if asbool(request.params.get('soft')):
        expires = int(parse_qs(urlparse(location).query)['Expires'][0])
        return {
            '@type': ['SoftRedirect'],
            'location': location,
            'expires': datetime.datetime.fromtimestamp(expires, pytz.utc).isoformat(),
        }
    proxy = asbool(request.params.get('proxy'))
    accel_redirect_header = request.registry.settings.get('accel_redirect_header')
    if proxy and accel_redirect_header:
        return InternalRedirect(headers={accel_redirect_header: '/_proxy/' + str(location)})
    raise HTTPTemporaryRedirect(location=location)


@view_config(context=File, permission='edit_bucket', request_method='PATCH',
             name='update_bucket')
def file_update_bucket(context, request):
    new_bucket = request.json_body.get('new_bucket')
    if not new_bucket:
        raise ValidationFailure('body', ['bucket'], 'New bucket not specified')
    force = asbool(request.params.get('force'))
    known_buckets = [
        request.registry.settings['file_upload_bucket'],
        request.registry.settings['pds_public_bucket'],
        request.registry.settings['pds_private_bucket'],
    ]
    # Try to validate input to a known bucket.
    if new_bucket not in known_buckets and not force:
        raise ValidationFailure('body', ['bucket'], 'Unknown bucket and force not specified')
    current_bucket = context._get_external_sheet().get('bucket')
    # Don't bother setting if already the same.
    if current_bucket != new_bucket:
        request.registry.notify(BeforeModified(context, request))
        context._set_external_sheet({'bucket': new_bucket})
        request.registry.notify(AfterModified(context, request))
    return {
        'status': 'success',
        '@type': ['result'],
        'old_bucket': current_bucket,
        'new_bucket': new_bucket
    }
