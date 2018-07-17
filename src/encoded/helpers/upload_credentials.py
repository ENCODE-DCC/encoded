"""
Helper Class to encapsulate functionality needed for uploading files

The class UploadCredentials is exposed in __init__.py
"""
import boto3


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

    def _get_base_policy(self):
        resource_string = "arn:aws:s3:::{}".format(self._file_url)
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

    def _get_token(self, policy):
        conn = boto3.Session(profile_name=self._profile_name).client('sts')
        return = conn.get_federation_token(
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

    def external_creds(self):
        policy = self._get_base_policy()
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
