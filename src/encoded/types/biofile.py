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

    }

    embedded = [
        'platform',
        'bioreplicate',
       

    ]
    audit_inherit = [

    ]
    set_status_up = [
        'platform',

    ]
    set_status_down = []
    public_s3_statuses = ['released', 'archived']
    private_s3_statuses = ['in progress', 'replaced', 'deleted', 'revoked']

