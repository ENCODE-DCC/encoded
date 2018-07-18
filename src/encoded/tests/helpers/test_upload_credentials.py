from moto import mock_sts


@mock_sts
def test_external_creds():
    from encoded.helpers import external_creds
    creds = external_creds('mock_bucket', 'mock_object', 'mock_name')
    assert 'upload_credentials' in creds
    assert creds['bucket'] == 'mock_bucket'
    assert creds['key'] == 'mock_object'
    assert 'mock_name' in creds['upload_credentials']['federated_user_id']
    assert creds['service'] == 's3'
