from ..contentbase import location
from ..schema_utils import load_schema
from .views import (
    ACCESSION_KEYS,
    Collection,
)
from pyramid.traversal import find_root
import boto
import json
import time


def show_upload_credentials(request=None, context=None, status=None):
    if request is None or status != 'uploading':
        return False
    return request.has_permission('edit', context)


def external_creds(parent, properties):
    registry = find_root(parent).registry
    bucket = registry.settings['file_upload_bucket']
    key = '{uuid}/{accession}.{file_format}'.format(**properties)
    policy = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Sid': 'Stmt1',
                'Effect': 'Allow',
                'Action': 's3:PutObject',
                'Resource': 'arn:aws:s3:::{bucket}/{key}'.format(bucket=bucket, key=key),
            }
        ]
    }
    name = 'upload-{time}-{accession}'.format(time=time.time(), **properties)  # max 32 chars
    conn = boto.connect_sts()
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


@location('files')
class File(Collection):
    item_type = 'file'
    schema = load_schema('file.json')
    properties = {
        'title': 'Files',
        'description': 'Listing of Files',
    }

    class Item(Collection.Item):
        name_key = 'accession'
        keys = ACCESSION_KEYS  # + ALIAS_KEYS
        namespace_from_path = {
            'lab': 'dataset.lab',
            'award': 'dataset.award',
        }
        template = {
            'upload_credentials': {
                '$templated': True,
                '$condition': show_upload_credentials,
                '$value': lambda context: context.propsheets['external']['upload_credentials'],
            }
        }

        @classmethod
        def create(cls, parent, uuid, properties, sheets=None):
            if properties.get('status') == 'uploading':
                sheets = {} if sheets is None else sheets.copy()
                sheets['external'] = external_creds(parent, properties)
            return super(File.Item, cls).create(parent, uuid, properties, sheets)
