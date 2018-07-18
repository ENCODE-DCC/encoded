import boto3
import json


class UploadCredentials(object):

    def __init__(self, bucket, key, name, profile_name=None):
        self._bucket = bucket
        self._key = key
        self._name = name
        self._profile_name = profile_name

    def external_creds(self):
        bucket = self._bucket
        key = self._key
        name = self._name
        profile_name = self._profile_name
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
        conn = boto3.Session(profile_name=profile_name).client('sts')
        token = conn.get_federation_token(
            Name=name,
            Policy=json.dumps(policy)
        )
        # 'access_key' 'secret_key' 'expiration' 'session_token'
        creds = token.get('Credentials', {})
        # Maintain boto field names.
        credentials = {
            'session_token': creds.get('SessionToken'),
            'access_key': creds.get('AccessKeyId'),
            'expiration': creds.get('Expiration').isoformat(),
            'secret_key': creds.get('SecretAccessKey'),
            'upload_url': 's3://{bucket}/{key}'.format(bucket=bucket, key=key),
            'federated_user_arn': token.get('FederatedUser', {}).get('Arn'),
            'federated_user_id': token.get('FederatedUser', {}).get('FederatedUserId'),
            'request_id': token.get('ResponseMetadata', {}).get('RequestId')
        }
        return {
            'service': 's3',
            'bucket': bucket,
            'key': key,
            'upload_credentials': credentials,
        }
