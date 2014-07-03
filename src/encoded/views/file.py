from ..contentbase import location
from ..schema_utils import load_schema
from .views import (
    ACCESSION_KEYS,
    Collection,
)
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)
from pyramid.traversal import find_root
from pyramid.view import view_config
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
    mapping = parent.schema['file_format_file_extension']
    file_extension = mapping[properties['file_format']]
    key = '{uuid}/{accession}{file_extension}'.format(**properties)
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
            ns = Collection.Item.template_namespace(self, properties, request)
            if 'download_path' in properties:
                path = properties['download_path']
                ns['file_extension'] = path[path.find('.', path.rfind('/')):]
            else:
                mapping = self.schema['file_format_file_extension']
                ns['file_extension'] = mapping[properties['file_format']]
            return ns

        @classmethod
        def create(cls, parent, uuid, properties, sheets=None):
            if properties.get('status') == 'uploading':
                sheets = {} if sheets is None else sheets.copy()
                sheets['external'] = external_creds(parent, properties)
            return super(File.Item, cls).create(parent, uuid, properties, sheets)


@view_config(name='download', context=File.Item, request_method='GET',
             permission='view', subpath_segments=[0, 1])
def download(context, request):
    properties = context.upgrade_properties(finalize=False)
    ns = context.template_namespace(properties, request)
    if request.subpath:
        filename, = request.subpath
        if filename != '{accession}{file_extension}'.format(**ns):
            raise HTTPNotFound(filename)

    external = context.propsheets.get('external')
    if external is None:  # EDW
        location = 'http://encodedcc.sdsc.edu/warehouse/{download_path}'.format(**ns)
    elif external['service'] == 's3':
        conn = boto.connect_s3()
        location = conn.generate_url(36*60*60, 'GET', external['bucket'], external['key'])
    else:
        raise ValueError(external['service'])

    raise HTTPFound(location=location)
