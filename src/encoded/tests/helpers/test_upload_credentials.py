from unittest import TestCase

import pytest

from moto import mock_sts

from encoded.helpers import UploadCredentials
from encoded.helpers import EXTERNAL_BUCKET_STATEMENTS

from . import HELPERS_DATA_PATH


@mock_sts
def test_external_creds():
    from encoded.helpers import UploadCredentials
    upload_creds = UploadCredentials(
        'mock_bucket',
        'mock_object',
        'mock_name',
    )
    creds = upload_creds.external_creds()
    assert 'upload_credentials' in creds
    assert creds['bucket'] == 'mock_bucket'
    assert creds['key'] == 'mock_object'
    assert 'mock_name' in creds['upload_credentials']['federated_user_id']
    assert creds['service'] == 's3'


class TestUploadCredentials(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._upload_creds_attrs = [
            '_bucket',
            '_key',
            '_name',
            '_profile_name',
            '_resource_string',
            '_upload_url',
            '_external_policy',
        ]
        cls._external_creds_keys = ['service', 'bucket', 'key', 'upload_credentials']
        cls._credentials_keys = [
            'session_token', 'access_key', 'expiration', 'secret_key',
            'upload_url', 'federated_user_arn', 'federated_user_id','request_id',
        ]
        cls._test_bucket = 'mock_bucket'
        cls._test_key = 'mock_key'
        cls._test_name = 'mock_name'
        cls._test_profile_name = 'mock_profile_name'
        cls._default_upload_creds = UploadCredentials(
            cls._test_bucket,
            cls._test_key,
            cls._test_name,
            cls._test_profile_name,
        )

    def test_init_attributes_missing(self):
        for attribute in self._upload_creds_attrs:
            self.assertTrue(hasattr(self._default_upload_creds, attribute))

    def test_init_attribute_values(self):
        self.assertEqual(self._test_bucket, self._default_upload_creds._bucket)
        self.assertEqual(self._test_key, self._default_upload_creds._key)
        self.assertEqual(self._test_name, self._default_upload_creds._name)
        self.assertEqual(self._test_profile_name, self._default_upload_creds._profile_name)
        self.assertEqual(
            "arn:aws:s3:::{bucket}/{key}".format(
                bucket=self._test_bucket,
                key=self._test_key
            ),
            self._default_upload_creds._resource_string
        )
        self.assertEqual(
            "s3://{bucket}/{key}".format(
                bucket=self._test_bucket,
                key=self._test_key
            ),
            self._default_upload_creds._upload_url
        )

    def test_init_profile_name_none(self):
        upload_creds = UploadCredentials(
            self._test_bucket,
            self._test_key,
            self._test_name
        )
        self.assertIsNone(upload_creds._profile_name)

    def test_init_external_policy_empty(self):
        upload_creds = UploadCredentials(self._test_bucket, self._test_key, self._test_name)
        self.assertTrue(isinstance(upload_creds._external_policy, dict))
        self.assertFalse(upload_creds._external_policy)

    def test_get_policy(self):
        test_result = self._default_upload_creds._get_policy()
        self.assertTrue(isinstance(test_result, dict))
        self.assertTrue('Statement' in test_result)
        statements = test_result['Statement']
        self.assertTrue(isinstance(statements, list))
        self.assertEqual(len(statements), 1)
        statement_item = statements[0]
        self.assertEqual('Allow',  statement_item.get('Effect'))
        self.assertEqual('s3:PutObject',  statement_item.get('Action'))
        self.assertEqual(
            self._default_upload_creds._resource_string,
            statement_item.get('Resource')
        )

    def test_get_policy_no_external(self):
        upload_creds = UploadCredentials(
            self._test_bucket,
            self._test_key,
            self._test_name,
            self._test_profile_name,
        )
        self.assertDictEqual(
            upload_creds._get_base_policy(),
            upload_creds._get_policy()
        )

    def test_get_policy_no_statement(self):
        upload_creds = UploadCredentials(self._test_bucket, self._test_key, self._test_name)
        for item in [
            {'NotStatement': ['a']},
            {'Statement': {}},
            {'Statement': []},
            {'Statement': None},
            {'Statement': 'a'},
        ]:
            upload_creds._external_policy = item
            self.assertDictEqual(
                upload_creds._get_base_policy(),
                upload_creds._get_policy(),
            )

    def test_get_policy_external_statement(self):
        upload_creds = UploadCredentials(self._test_bucket, self._test_key, self._test_name)
        for policy in [
            {'Statement': ['a']},
            {'Statement': ['a', 'b', 'c']},
        ]:
            upload_creds._external_policy = policy
            base = upload_creds._get_base_policy()
            for statement in policy['Statement']:
                base['Statement'].append(statement)
            self.assertDictEqual(
                base,
                upload_creds._get_policy(),
            )

    def test_get_token_mock(self):
        policy = self._default_upload_creds._get_policy()
        token = self._default_upload_creds._get_token(policy)
        self.assertIsNone(token)

    def test_get_token_default(self):
        upload_creds = UploadCredentials(
            self._test_bucket,
            self._test_key,
            self._test_name,
            profile_name='default',
        )
        policy = upload_creds._get_policy()
        token = upload_creds._get_token(policy)
        self.assertTrue(isinstance(token, dict))

    def test_check_external_policy_zero(self):
        upload_creds = UploadCredentials(
            self._test_bucket,
            self._test_key,
            self._test_name,
            self._test_profile_name,
        )
        for allow, bucket_list_path in [
                (False, None),
                (True, None),
                (False, 'some-path'),
                (True, 'bad-path'),
                (True, HELPERS_DATA_PATH + '/' + 'external_bucket_list_empty'),
        ]:
            upload_creds._check_external_policy(
                allow=allow,
                bucket_list_path=bucket_list_path
            )
            self.assertDictEqual(upload_creds._external_policy, {})

    def test_external_bucket_policies(self):
        '''
        Placed here for debugging, should exist outside class
        '''
        expected_actions = ['s3:GetObject', 's3:ListBucket', 's3:GetObjectAcl']
        result_actions = []
        for statement in EXTERNAL_BUCKET_STATEMENTS:
            self.assertTrue('Action' in statement)
            self.assertTrue(isinstance(statement['Action'], str))
            result_actions.append(statement['Action'])
            self.assertTrue('Resource' in statement)
            self.assertTrue(callable(statement['Resource']))
            resource_str = statement['Resource']('some-bucket-name')
            self.assertTrue(isinstance(resource_str, str))
            self.assertTrue('Effect' in statement)
            self.assertEqual(statement['Effect'], 'Allow')
        self.assertListEqual(expected_actions, result_actions)

    def test_check_external_policy_one(self):
        import os
        expected_bucket_names = ['test-bucket-one']
        upload_creds = UploadCredentials(
            self._test_bucket,
            self._test_key,
            self._test_name,
            self._test_profile_name,
        )
        for allow, bucket_list_path in [
                (True, HELPERS_DATA_PATH + '/' + 'external_bucket_list_one'),
        ]:
            upload_creds._check_external_policy(
                allow=allow,
                bucket_list_path=bucket_list_path
            )
            os.remove(bucket_list_path + '.json')
            expected_resources = {
                's3:GetObject': [
                    'arn:aws:s3:::%s/*' % item for item in expected_bucket_names
                ],
                's3:ListBucket': [
                    'arn:aws:s3:::%s' % item for item in expected_bucket_names
                ],
                's3:GetObjectAcl': [
                    'arn:aws:s3:::%s/*' % item for item in expected_bucket_names
                ],
            }
            result_statements = upload_creds._external_policy['Statement']
            self.assertEqual(len(result_statements), len(EXTERNAL_BUCKET_STATEMENTS))
            for result_statement in result_statements:
                resources = result_statement['Resource']
                self.assertTrue(isinstance(resources, list))
                self.assertEqual(len(resources), 1)
                self.assertListEqual(
                    expected_resources[result_statement['Action']],
                    result_statement['Resource']
                )

    def test_check_external_policy_many(self):
        import os
        expected_bucket_names = [
            'test-bucket-one',
            'test-bucket-two',
            'test-bucket-three',
        ]
        upload_creds = UploadCredentials(
            self._test_bucket,
            self._test_key,
            self._test_name,
            self._test_profile_name,
        )
        for allow, bucket_list_path in [
                (True, HELPERS_DATA_PATH + '/' + 'external_bucket_list_many'),
        ]:
            upload_creds._check_external_policy(
                allow=allow,
                bucket_list_path=bucket_list_path
            )
            os.remove(bucket_list_path + '.json')
            expected_resources = {
                's3:GetObject': [
                    'arn:aws:s3:::%s/*' % item for item in expected_bucket_names
                ],
                's3:ListBucket': [
                    'arn:aws:s3:::%s' % item for item in expected_bucket_names
                ],
                's3:GetObjectAcl': [
                    'arn:aws:s3:::%s/*' % item for item in expected_bucket_names
                ],
            }
            result_statements = upload_creds._external_policy['Statement']
            self.assertEqual(len(result_statements), len(EXTERNAL_BUCKET_STATEMENTS))
            for result_statement in result_statements:
                resources = result_statement['Resource']
                self.assertTrue(isinstance(resources, list))
                self.assertEqual(len(resources), 3)
                self.assertListEqual(
                    expected_resources[result_statement['Action']],
                    result_statement['Resource']
                )

    def test_external_creds_keys(self):
        upload_creds = UploadCredentials(
            self._test_bucket,
            self._test_key,
            self._test_name,
            profile_name='default',
        )
        creds_dict = upload_creds.external_creds()
        self.assertListEqual(
            sorted(self._external_creds_keys),
            sorted(list(creds_dict.keys()))
        )
        upload_credentials = creds_dict['upload_credentials']
        self.assertTrue(isinstance(upload_credentials, dict))
        self.assertListEqual(
            sorted(self._credentials_keys),
            sorted(list(upload_credentials.keys()))
        )

    def test_external_creds_values(self):
        upload_creds = UploadCredentials(
            self._test_bucket,
            self._test_key,
            self._test_name,
            profile_name='default',
        )
        creds_dict = upload_creds.external_creds()
        self.assertEqual(creds_dict['service'], 's3')
        self.assertEqual(creds_dict['bucket'], self._test_bucket)
        self.assertEqual(creds_dict['key'], self._test_key)
        upload_credentials = creds_dict['upload_credentials']
        self.assertEqual(
            upload_credentials['upload_url'],
            upload_creds._upload_url
        )
