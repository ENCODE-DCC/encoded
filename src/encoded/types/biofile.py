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
from snovault.schema_utils import schema_validator
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
from pyramid.response import Response
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


@collection(
    name='biofiles',
    unique_key='accession',
    properties={
        'title': 'Biofiles',
        'description': 'Listing of Files',
    })
class Biofile(Item):
    item_type = 'biofile'
    schema = load_schema('encoded:schemas/biofile.json')
    name_key = 'accession'
    rev = {
        'paired_with': ('Biofile', 'paired_with'),
        'superseded_by': ('Biofile', 'supersedes'),
    }
    embedded = [
        'platform',
        'award',
        'bioreplicate',
        'bioreplicate.bioexperiment',
        'bioreplicate.biolibrary',
        'submitted_by',
    ]
    audit_inherit = [
    ]
    set_status_up = [
        'platform',

    ]
    set_status_down = []
    public_s3_statuses = ['released', 'archived']
    private_s3_statuses = ['in progress', 'replaced', 'deleted', 'revoked']

    @calculated_property(schema={
        "title": "Superseded by",
        "description": "The file(s) that supersede this file (i.e. are more preferable to use).",
        "comment": "Do not submit. Values in the list are reverse links of a file that supersedes.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Biofile.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(
        condition=lambda paired_end=None: paired_end == '1')
    def paired_with(self, root, request):
        paired_with = self.get_rev_links('paired_with')
        if not paired_with:
            return None
        item = root.get_by_uuid(paired_with[0])
        return request.resource_path(item)
