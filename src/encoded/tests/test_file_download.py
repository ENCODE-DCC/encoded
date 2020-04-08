import pytest
from moto import (
    mock_s3,
    mock_sts
)


@mock_sts
def test_uploading_file_credentials(testapp, uploading_file_0, dummy_request):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file_0)
    posted_file = res.json['@graph'][0]
    assert 'upload_credentials' in posted_file
    res = testapp.patch_json(posted_file['@id'], {'status': 'in progress'})
    updated_file = res.json['@graph'][0]
    assert 'upload_credentials' not in updated_file


@mock_sts
@mock_s3
def test_file_download_view_redirect(testapp, uploading_file_0, dummy_request):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file_0)
    posted_file = res.json['@graph'][0]
    res = testapp.get(
        posted_file['href'],
        extra_environ=dict(HTTP_X_FORWARDED_FOR='100.100.100.100')
    )
    assert '307 Temporary Redirect' in str(res.body)
    assert 'X-Accel-Redirect' not in res.headers
    assert all([x in res.headers['Location'] for x in ['s3', 'amazonaws', 'test_upload_bucket']])


@mock_sts
@mock_s3
def test_file_download_view_proxy_range(testapp, uploading_file_0, dummy_request):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file_0)
    posted_file = res.json['@graph'][0]
    res = testapp.get(
        posted_file['href'],
        headers=dict(Range='bytes=0-4444'),
        extra_environ=dict(HTTP_X_FORWARDED_FOR='100.100.100.100')
    )
    assert '307 Temporary Redirect' in str(res.body)
    assert 'X-Accel-Redirect' not in res.headers


@mock_sts
@mock_s3
def test_file_download_view_soft_redirect(testapp, uploading_file_0, dummy_request):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file_0)
    posted_file = res.json['@graph'][0]
    res = testapp.get(
        posted_file['href'] + '?soft=True',
        extra_environ=dict(HTTP_X_FORWARDED_FOR='100.100.100.100')
    )
    assert res.json['@type'][0] == 'SoftRedirect'


@mock_sts
def test_regen_creds_uploading_file_not_found(testapp, uploading_file_0, dummy_request, root):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file_0)
    posted_file = res.json['@graph'][0]
    item = root.get_by_uuid(posted_file['uuid'])
    properties = item.upgrade_properties()
    # Clear the external sheet.
    item.update(properties, sheets={'external': {}})
    res = testapp.post_json(posted_file['@id'] + '@@upload', {}, status=404)


@mock_sts
@mock_s3
def test_download_file_not_found(testapp, uploading_file_0, dummy_request, root):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file_0)
    posted_file = res.json['@graph'][0]
    item = root.get_by_uuid(posted_file['uuid'])
    properties = item.upgrade_properties()
    # Clear the external sheet.
    item.update(properties, sheets={'external': {}})
    res = testapp.get(
        posted_file['href'],
        extra_environ=dict(HTTP_X_FORWARDED_FOR='100.100.100.100'),
        status=404
    )
