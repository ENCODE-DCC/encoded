from botocore.exceptions import ClientError
from botocore.config import Config
from snovault import (
    abstract_collection,
    AfterModified,
    BeforeModified,
    CONNECTION,
    calculated_property,
    collection,
    load_schema,
)
from snovault.attachment import InternalRedirect
from snovault.schema_utils import schema_validator
from snovault.validation import ValidationFailure
from .base import (
    Item,
    paths_filtered_by_status,
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

from urllib.parse import urlparse

from snovault.util import ensure_list_and_filter_none
from snovault.util import take_one_or_return_none
from snovault.util import try_to_get_field_from_item_with_skip_calculated_first


def inherit_protocol_prop(request, seqrun_id, propname, read_type):
    seqrun_obj = request.embed(seqrun_id, '@@object?skip_calculated=true')
    lib_id = seqrun_obj.get('derived_from')
    lib_obj = request.embed(lib_id, '@@object?skip_calculated=true')
    libprot_id = lib_obj.get('protocol')
    libprot_obj = request.embed(libprot_id, '@@object?skip_calculated=true')
    if 'sequence_file_standards' in libprot_obj:
        standards = libprot_obj.get('sequence_file_standards')
        for s in standards:
            if s.get('read_type') == read_type:
                return s.get(propname)


RAW_OUTPUT_TYPES = ['reads', 'rejected reads', 'raw data', 'reporter code counts', 'intensity values', 'idat red channel', 'idat green channel']


def file_is_md5sum_constrained(properties):
    conditions = [
        properties.get('output_type') in RAW_OUTPUT_TYPES
    ]
    return any(conditions)


@abstract_collection(
    name='files',
    unique_key='title',
    properties={
        'title': 'Files',
        'description': 'Listing of all types of file.',
    })
class File(Item):
    base_types = ['File'] + Item.base_types
    embedded = []

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


    @calculated_property(schema={
        "title": "Download URL",
        "description": "The download path for S3 to obtain the actual file.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
    })
    def href(self, request, file_format, accession=None, external_accession=None):
        accession = accession or external_accession
        file_extension = self.schema['file_format_file_extension'][file_format]
        filename = '{}{}'.format(accession, file_extension)
        return request.resource_path(self, '@@download', filename)


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

    if properties.get('external_uri'):
        raise HTTPTemporaryRedirect(location=properties.get('external_uri'))

    if properties.get('s3_uri'):
        conn = boto3.client('s3')

        parsed_href = urlparse(properties.get('s3_uri'), allow_fragments=False)
        bucket = parsed_href.netloc
        key    = parsed_href.path.lstrip('/')

        location = conn.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket,
                'Key': key,
                'ResponseContentDisposition': 'attachment; filename=' + filename
            },
            ExpiresIn=36*60*60
        )
    else:
        raise HTTPNotFound(
            detail='S3 URI not present'
        )
    if asbool(request.params.get('soft')):
        expires = int(parse_qs(urlparse(location).query)['Expires'][0])
        return {
            '@type': ['SoftRedirect'],
            'location': location,
            'expires': datetime.datetime.fromtimestamp(expires, pytz.utc).isoformat(),
        }
    raise HTTPTemporaryRedirect(location=location)


@abstract_collection(
    name='data-files',
    unique_key='accession',
    properties={
        'title': 'Data Files',
        'description': 'Listing of all types of data file.',
    })
class DataFile(File):
    item_type = 'data_file'
    base_types = ['DataFile'] + File.base_types
    name_key = 'accession'
    rev = {
        'superseded_by': ('DataFile', 'supersedes'),
        'quality_metrics': ('Metrics', 'quality_metric_of'),
    }
    embedded = File.embedded + ['lab', 'award']
    public_s3_statuses = ['released', 'archived']
    private_s3_statuses = ['in progress', 'replaced', 'deleted', 'revoked']


    @calculated_property(schema={
        "title": "Read length units",
        "description": "The units for read length.",
        "comment": "Do not submit. This is a calculated property",
        "type": "string",
        "enum": [
            "nt"
        ]
    })
    def read_length_units(self, read_length=None, mapped_read_length=None):
        if read_length is not None or mapped_read_length is not None:
            return "nt"


    @calculated_property(schema={
        "title": "Award",
        "description": "The HCA Seed Network or HCA Pilot Project award used to fund this data generation.",
        "comment": "Do not submit. This is a calculated property.",
        "type": "string",
        "linkTo": "Award"
    })
    def award(self, request, dataset):
        dataset_obj = request.embed(dataset, '@@object?skip_calculated=true')
        return dataset_obj.get('award')


    @calculated_property(schema={
        "title": "Superseded by",
        "description": "The file(s) that supersede this file (i.e. are more preferable to use).",
        "comment": "Do not submit. This is a calculated property",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "DataFile.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)


@abstract_collection(
    name='analysis-files',
    unique_key='accession',
    properties={
        'title': "Analysis Files",
        'description': "",
    })
class AnalysisFile(DataFile):
    item_type = 'analysis_file'
    base_types = ['AnalysisFile'] + DataFile.base_types
    schema = load_schema('encoded:schemas/analysis_file.json')
    embedded = DataFile.embedded + []


    @calculated_property(schema={
        "title": "Quality metrics",
        "description": "The list of QC metric objects associated with this file.",
        "comment": "Do not submit. Values in the list are reverse links of a quality metric with this file in quality_metric_of field.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Metrics.quality_metric_of",
        },
        "notSubmittable": True,
    })
    def quality_metrics(self, request, quality_metrics):
        return paths_filtered_by_status(request, quality_metrics)


    @calculated_property(define=True,
                         schema={"title": "Libraries",
                                 "description": "The libraries the file was derived from.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "array",
                                 "items": {
                                    "type": "string",
                                    "linkTo": "Library"
                                    }
                                })
    def libraries(self, request, derived_from):
        all_libs = set()
        for f in derived_from:
            obj = request.embed(f, '@@object')
            if obj.get('library'):
                all_libs.add(obj.get('library'))
            elif obj.get('libraries'):
                all_libs.update(obj.get('libraries'))
            elif obj.get('protocol'):
                all_libs.add(obj.get('@id'))
        return sorted(all_libs)


@collection(
    name='sequence-alignment-files',
    unique_key='accession',
    properties={
        'title': "Sequence Alignment Files",
        'description': "",
    })
class SequenceAlignmentFile(AnalysisFile):
    item_type = 'sequence_alignment_file'
    schema = load_schema('encoded:schemas/sequence_alignment_file.json')
    embedded = AnalysisFile.embedded + []


@collection(
    name='raw-sequence-files',
    unique_key='accession',
    properties={
        'title': "Raw Sequence Files",
        'description': "",
    })
class RawSequenceFile(DataFile):
    item_type = 'raw_sequence_file'
    schema = load_schema('encoded:schemas/raw_sequence_file.json')
    embedded = DataFile.embedded + []

    @calculated_property(define=True,
                         schema={"title": "Libraries",
                                 "description": "The library the file was derived from.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "array",
                                 "items": {
                                     "type": "string",
                                     "linkTo": "Library"
                                 }
                                })
    def libraries(self, request, derived_from):
        seqrun_obj = request.embed(derived_from, '@@object?skip_calculated=true')
        lib_id = seqrun_obj.get('derived_from')
        return [lib_id]


    @calculated_property(define=True,
                         schema={"title": "Sequence elements",
                                 "description": "The biological content of the sequence reads.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "array",
                                 "items": {
                                    "type": "string"
                                 }
                                })
    def sequence_elements(self, request, derived_from=None, read_type=None):
        return inherit_protocol_prop(request, derived_from, 'sequence_elements', read_type)


    @calculated_property(define=True,
                         schema={"title": "Demultiplexed type",
                                 "description": "The read assignment after sample demultiplexing for fastq files.",
                                 "comment": "Do not submit. This is a calculated property",
                                 "type": "string"
                                })
    def demultiplexed_type(self, request, derived_from=None, read_type=None):
        return inherit_protocol_prop(request, derived_from, 'demultiplexed_type', read_type)


@collection(
    name='matrix-files',
    unique_key='accession',
    properties={
        'title': "Matrix Files",
        'description': "",
    })
class MatrixFile(AnalysisFile):
    item_type = 'matrix_file'
    schema = load_schema('encoded:schemas/matrix_file.json')
    embedded = AnalysisFile.embedded + []


@collection(
    name='reference-files',
    unique_key='accession',
    properties={
        'title': "Reference Files",
        'description': "",
    })
class ReferenceFile(File):
    item_type = 'reference_file'
    schema = load_schema('encoded:schemas/reference_file.json')
    embedded = File.embedded + ['organism']
