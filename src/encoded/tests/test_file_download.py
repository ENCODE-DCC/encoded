import pytest
from moto import (
    mock_s3,
    mock_sts
)


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


def test_uploading_file_credentials(testapp, uploading_file, dummy_request):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    posted_file = res.json['@graph'][0]
    assert 'upload_credentials' in posted_file
    res = testapp.patch_json(posted_file['@id'], {'status': 'in progress'})
    updated_file = res.json['@graph'][0]
    assert 'upload_credentials' not in updated_file


@mock_s3
def test_file_download_view_redirect(testapp, uploading_file, dummy_request):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    posted_file = res.json['@graph'][0]
    res = testapp.get(
        posted_file['href'],
        extra_environ=dict(HTTP_X_FORWARDED_FOR='100.100.100.100')
    )
    assert '307 Temporary Redirect' in str(res.body)
    assert 'X-Accel-Redirect' not in res.headers
    assert 'https://s3.us-west-2.amazonaws.com/test_upload_bucket/' in res.headers['Location']


@mock_s3
def test_file_download_view_proxy_range(testapp, uploading_file, dummy_request):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    posted_file = res.json['@graph'][0]
    res = testapp.get(
        posted_file['href'],
        headers=dict(Range='bytes=0-4444'),
        extra_environ=dict(HTTP_X_FORWARDED_FOR='100.100.100.100')
    )
    assert 'X-Accel-Redirect' in res.headers


@mock_s3
def test_file_download_view_soft_redirect(testapp, uploading_file, dummy_request):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    posted_file = res.json['@graph'][0]
    res = testapp.get(
        posted_file['href'] + '?soft=True',
        extra_environ=dict(HTTP_X_FORWARDED_FOR='100.100.100.100')
    )
    assert res.json['@type'][0] == 'SoftRedirect'
