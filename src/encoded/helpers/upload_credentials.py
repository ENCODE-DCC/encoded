import boto3
import botocore
import json


class UploadCredentials(object):

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

    def _get_policy(self):
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

    def _get_token(self, policy):
        try:
            conn = boto3.Session(profile_name=self._profile_name).client('sts')
        except botocore.exceptions.ProfileNotFound as ecp:
            print('Warning: ', ecp)
            return None
        try:
            token = conn.get_federation_token(
                Name=self._name,
                Policy=json.dumps(policy)
            )
            return token
        except botocore.exceptions.ClientError as ecp:
            print('Warning: ', ecp)
            return None

    def external_creds(self):
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
