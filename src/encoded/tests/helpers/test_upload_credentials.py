from unittest import TestCase

import pytest

from encoded.helpers import UploadCredentials


class TestUploadCredentials(TestCase):

    @classmethod
    def setUpClass(cls):
        cls._upload_creds_attrs = [
            '_bucket',
            '_key',
            '_name',
            '_profile_name',
            '_file_url',
            '_resource_string',
            '_external_policy',
        ]
        cls.test_bucket = 'some-bucket-name'
        cls.test_key = 'file-to-upload-key'
        cls.test_name = 'fed-token-name'
        cls.test_profile_name = 'some-profile-name'
        cls._upload_creds = UploadCredentials(
            cls.test_bucket,
            cls.test_key,
            cls.test_name,
            cls.test_profile_name,
        )

    def test_init_attributes_missing(self):
        upload_creds = self._upload_creds
        for attribute in self._upload_creds_attrs:
            self.assertTrue(hasattr(upload_creds, attribute))

    def test_init_attribute_values(self):
        upload_creds = self._upload_creds
        self.assertEqual(self.test_bucket, upload_creds._bucket)
        self.assertEqual(self.test_key, upload_creds._key)
        self.assertEqual(self.test_name, upload_creds._name)
        self.assertEqual(self.test_profile_name, upload_creds._profile_name)
        self.assertEqual(
            "{bucket}/{key}".format(
                bucket=self.test_bucket,
                key=self.test_key
            ),
            upload_creds._file_url
        )
        self.assertEqual(
            "arn:aws:s3:::{bucket}/{key}".format(
                bucket=self.test_bucket,
                key=self.test_key
            ),
            upload_creds._resource_string
        )

    def test_init_profile_name_none(self):
        upload_creds = UploadCredentials(self.test_bucket, self.test_key, self.test_name)
        self.assertIsNone(upload_creds._profile_name)

    def test_init_external_policy_none(self):
        upload_creds = UploadCredentials(self.test_bucket, self.test_key, self.test_name)
        self.assertIsNone(upload_creds._external_policy)

    def test_get_base_policy(self):
        test_result = self._upload_creds._get_base_policy()
        self.assertTrue(isinstance(test_result, dict))
        self.assertTrue('Statement' in test_result)
        statements = test_result['Statement']
        self.assertTrue(isinstance(statements, list))
        self.assertEqual(len(statements), 1)
        statement_item = statements[0]
        self.assertEqual('Allow',  statement_item.get('Effect'))
        self.assertEqual('s3:PutObject',  statement_item.get('Action'))
        self.assertEqual(self._upload_creds._resource_string,  statement_item.get('Resource'))

    def test_get_policy_no_external(self):
        self.assertDictEqual(
            self._upload_creds._get_base_policy(),
            self._upload_creds._get_policy()
        )

    def test_get_policy_external_false(self):
        test_bucket_list_path = 'some-path'
        upload_creds = UploadCredentials(self.test_bucket, self.test_key, self.test_name)
        upload_creds.check_external_policy(
            allow=True,
            bucket_list_path=test_bucket_list_path,
        )
        self.assertDictEqual(
            self._upload_creds._get_base_policy(),
            self._upload_creds._get_policy()
        )
        print('check call count')
        asert False

    # def test_get_policy_external_no_path(self):
    # def test_get_policy_external_bad_path(self):
    # def test_get_policy_external_empty(self):
    # def test_get_policy_external_one(self):
    def _test_get_policy_external_many(self):
        test_bucket_list_path = './data/bucket_list_many'
        upload_creds = UploadCredentials(self.test_bucket, self.test_key, self.test_name)
        upload_creds.check_external_policy(
            allow=True,
            bucket_list_path=test_bucket_list_path,
        )
        policy = self._upload_creds._get_policy()
        print(policy)
        assert False
