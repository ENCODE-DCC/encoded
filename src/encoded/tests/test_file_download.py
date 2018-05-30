import pytest
from moto import mock_s3
from moto import mock_sts


@pytest.fixture
def uploading_file(testapp, award, experiment, lab, replicate, dummy_request):
    item = {
        'award': award['@id'],
        'dataset': experiment['@id'],
        'lab': lab['@id'],
        'replicate': replicate['@id'],
        'file_format': 'tsv',
        'file_size': 2534535,
        'md5sum': '00000000000000000000000000000000',
        'output_type': 'raw data',
        'status': 'uploading',
    }
    return item


@mock_sts
def test_external_creds():
    from encoded.types.file import external_creds
    creds = external_creds('mock_bucket', 'mock_object', 'mock_name')
    assert 'upload_credentials' in creds
    assert creds['bucket'] == 'mock_bucket'


def test_file_download(testapp, uploading_file, dummy_request):
    pass


def test_uploading_file_credentials(testapp, uploading_file, dummy_request):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    posted_file = res.json['@graph'][0]
    assert 'upload_credentials' in posted_file
    res = testapp.patch_json(posted_file['@id'], {'status': 'in progress'})
    updated_file = res.json['@graph'][0]
    assert 'upload_credentials' not in updated_file
