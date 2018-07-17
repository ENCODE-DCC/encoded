"""
Helper Class to encapsulate functionality needed for uploading files

The class UploadCredentials is exposed in __init__.py
"""
import boto3


_EXTERNAL_BUCKET_POLICIES = [
    {
        'Action': 's3:GetObject',
        'Resource': lambda s: 'arn:aws:s3:::%s/*' % s,
        'Effect': 'Allow',
    },
    {
        'Action': 's3:ListBucket',
        'Resource': lambda s: 'arn:aws:s3:::%s' % s,
        'Effect': 'Allow',
    },
    {
        'Action': 's3:GetObjectAcl',
        'Resource': lambda s: 'arn:aws:s3:::%s/*' % s,
        'Effect': 'Allow',
    }
]


def _compile_statements_from_list(buckets_list):
    statements = []
    for ext_policy in EXTERNAL_BUCKET_POLICIES:
        new_policy = copy.copy(ext_policy)
        new_policy['Resource'] = []
        for line in lines:
            line = line.strip()
            if line:
                line = line.strip()
                new_policy['Resource'].append(ext_policy['Resource'](line))
        statements.append(new_policy)


def _save_policy_json(policy_json, file_path):
    with open(file_path + '.json', 'w') as file_handler:
        json.dump(policy_json, file_handler)


def _build_external_bucket_json(file_path):
    policy_json = {
        'Version': '2012-10-17',
        'Statement': [],
    }
    try:
        with open(file_path) as file_handler:
            buckets_list = [item.strip() for item in file_handler.readlines()]
            statements = _compile_statements_from_list(buckets_list)
            policy_json['Statement'] = statements
    except FileNotFoundError:
        print(
            'encoded.types.file.py.get_external_bucket_policy: '
            'Could not load external bucket policy list.'
        )
    _save_policy_json(policy_json, file_path)
    return policy_json


def _get_external_bucket_policy(file_path, retry=False):
    '''
    Returns a compiled json of external s3 access policies for federated users

    Checks if the policy json was already compiled on this instance.  If not,
    looks for the bucket list to compile and create the policy json.

    Returns
        -A policy json with EXTERNAL_BUCKET_POLICIES statements for each
        external bucket in the buckt list.
        -A policy json with zero statements if neither file is found

    Can be updated on the fly.  Just append bucket names to file_path
    and delete the created json file.
    '''
    try:
        with open(file_path) as file_handler:
            return json.loads(file_handler.read())
    except FileNotFoundError:
        if retry:
            _build_external_bucket_json(file_path)
            return _get_external_bucket_policy(file_path)


class UploadCredentials(object):
    def __init__(self, bucket, key, name, profile_name=None):
        self._bucket = bucket
        self._key = key
        self._name = name
        self._profile_name = profile_name
        self._file_url = "{bucket}/{key}".format(
            bucket=self._bucket,
            key=self._key
        )
        self._resource_string = "arn:aws:s3:::{}".format(self._file_url)
        self._external_policy = None

    def _get_base_policy(self):
        return {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Action': 's3:PutObject',
                    'Resource': self._resource_string,
                }
            ]
        }

    def _get_policy(self):
        policy = self._get_base_policy()
        if self._external_policy:
            for statement in self._external_policy.get('Statement', []):
                policy['Statement'].append(statement)
        return policy

    def _get_token(self, policy):
        conn = boto3.Session(profile_name=self._profile_name).client('sts')
        return conn.get_federation_token(
            Name=self._name,
            Policy=json.dumps(policy)
        )

    def _get_credentials(self):
        creds = token.get('Credentials', {})
        return {
            'session_token': creds.get('SessionToken'),
            'access_key': creds.get('AccessKeyId'),
            'expiration': creds.get('Expiration').isoformat(),
            'secret_key': creds.get('SecretAccessKey'),
        }

    def check_external_policy(self, allow=False, bucket_list_path=None):
        if allow and bucket_list_path:
            self._external_policy = _get_external_bucket_policy(bucket_list_path)

    def external_creds(self):
        policy = self._get_policy()
        token = self._get_token()
        credentials = self._get_credentials()
        credentials['upload_url'] = "s3://{}".format(self._file_url)
        credentials['federated_user_arn'] = token.get('FederatedUser', {}).get('Arn')
        credentials['federated_user_id'] = token.get('FederatedUser', {}).get('FederatedUserId')
        credentials['request_id'] = token.get('ResponseMetadata', {}).get('RequestId')
        return {
            'service': 's3',
            'bucket': self._bucket,
            'key': self._key,
            'upload_credentials': credentials,
        }
