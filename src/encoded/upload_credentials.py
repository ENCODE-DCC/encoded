"""
Helper class to create user credentials to upload files to s3
"""
import copy
import json

import boto3
import botocore


EXTERNAL_BUCKET_STATEMENTS = [
    {
        'Action': 's3:GetObject',
        'Resource': lambda s: 'arn:aws:s3:::%s/*' % s,
        'Effect': 'Allow',
    },
    {
        'Action': 's3:GetObjectAcl',
        'Resource': lambda s: 'arn:aws:s3:::%s/*' % s,
        'Effect': 'Allow',
    },
]
_FEDERATION_TOKEN_DURATION_SECONDS = 36 * 60 * 60


def _compile_statements_from_list(buckets_list):
    statements = []
    if buckets_list:
        for ext_policy in EXTERNAL_BUCKET_STATEMENTS:
            new_policy = copy.copy(ext_policy)
            new_policy['Resource'] = []
            for line in buckets_list:
                line = line.strip()
                if line:
                    line = line.strip()
                    new_policy['Resource'].append(ext_policy['Resource'](line))
            statements.append(new_policy)
    return statements


def _save_policy_json(policy_json, file_path):
    with open(file_path + '.json', 'w') as file_handler:
        json.dump(policy_json, file_handler)


def _build_external_bucket_json(file_path):
    try:
        with open(file_path) as file_handler:
            policy_json = {
                'Version': '2012-10-17',
                'Statement': [],
            }
            buckets_list = [item.strip() for item in file_handler.readlines()]
            statements = _compile_statements_from_list(buckets_list)
            if statements:
                policy_json['Statement'] = statements
                _save_policy_json(policy_json, file_path)
    except FileNotFoundError:  # pylint: disable=undefined-variable
        print(
            'encoded.types.file.py.get_external_bucket_policy: '
            'Could not load external bucket policy list.'
        )

def _get_external_bucket_policy(file_path):
    '''
    Returns a compiled json of external s3 access policies for federated users
    '''
    try:
        with open(file_path + '.json', 'r') as file_handler:
            return json.loads(file_handler.read())
    except FileNotFoundError:  # pylint: disable=undefined-variable
        return None


class UploadCredentials(object):
    # pylint: disable=too-few-public-methods
    '''
    Build and distribute federate aws credentials for submitting files
    '''
    def __init__(self, bucket, key, name, profile_name=None):
        self._bucket = bucket
        self._key = key
        self._name = name
        self._profile_name = profile_name
        file_url = "{bucket}/{key}".format(
            bucket=self._bucket,
            key=self._key
        )
        self._resource_string = "arn:aws:s3:::{}".format(file_url)
        self._upload_url = "s3://{}".format(file_url)
        self._external_policy = {}

    def _get_base_policy(self):
        policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Action': 's3:PutObject',
                    'Resource': self._resource_string,
                }
            ]
        }
        return policy

    def _get_policy(self):
        policy = self._get_base_policy()
        if (
                self._external_policy and
                self._external_policy.get('Statement') and
                isinstance(self._external_policy['Statement'], list)
        ):
            for statement in self._external_policy['Statement']:
                policy['Statement'].append(statement)
        return policy

    def _get_token(self, policy):
        try:
            conn = boto3.Session(profile_name=self._profile_name).client('sts')
        except botocore.exceptions.ProfileNotFound as ecp:
            print('Warning: ', ecp)
            return None
        try:
            token = conn.get_federation_token(
                Name=self._name,
                Policy=json.dumps(policy),
                DurationSeconds=_FEDERATION_TOKEN_DURATION_SECONDS,
            )
            return token
        except botocore.exceptions.ClientError as ecp:
            print('Warning: ', ecp)
            return None

    def _check_external_policy(self, s3_transfer_allow, s3_transfer_buckets):
        if s3_transfer_allow and s3_transfer_buckets:
            external_policy = _get_external_bucket_policy(s3_transfer_buckets)
            if not isinstance(external_policy, dict):
                _build_external_bucket_json(s3_transfer_buckets)
                external_policy = _get_external_bucket_policy(s3_transfer_buckets)
            if external_policy:
                self._external_policy = external_policy

    def external_creds(self, s3_transfer_allow=False, s3_transfer_buckets=None):
        '''
        Used to get the federate user credentials

        If external s3 buckets exist they will be added to the policy.
        '''
        self._check_external_policy(s3_transfer_allow, s3_transfer_buckets)
        policy = self._get_policy()
        token = self._get_token(policy)
        credentials = {
            'session_token': token.get('Credentials', {}).get('SessionToken'),
            'access_key': token.get('Credentials', {}).get('AccessKeyId'),
            'expiration': token.get('Credentials', {}).get('Expiration').isoformat(),
            'secret_key': token.get('Credentials', {}).get('SecretAccessKey'),
            'upload_url': self._upload_url,
            'federated_user_arn': token.get('FederatedUser', {}).get('Arn'),
            'federated_user_id': token.get('FederatedUser', {}).get('FederatedUserId'),
            'request_id': token.get('ResponseMetadata', {}).get('RequestId')
        }
        return {
            'service': 's3',
            'bucket': self._bucket,
            'key': self._key,
            'upload_credentials': credentials,
        }
