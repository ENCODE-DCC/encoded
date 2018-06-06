import pytest
from moto import (
    mock_s3,
    mock_sts
)
from pyramid.httpexceptions import HTTPNotFound

items = [
    {'description': 'item0'},
    {'description': 'item1'},
    {'description': 'item2'},
]


@pytest.fixture
def content(testapp):
    url = '/test-encode-items/'
    for item in items:
        testapp.post_json(url, item)


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


def test_item_set_status_method_exists(testapp, content, root):
    res = testapp.get('/test-encode-items/')
    encode_item_uuid = res.json['@graph'][0]['uuid']
    encode_item = root.get_by_uuid(encode_item_uuid)
    set_status_method = getattr(encode_item, 'set_status', None)
    assert callable(set_status_method)


def test_item_release_endpoint_calls_set_status(testapp, content, mocker):
    from encoded.types.base import Item
    res = testapp.get('/test-encode-items/')
    encode_item_id = res.json['@graph'][0]['@id']
    mocker.patch('encoded.types.base.Item.set_status')
    testapp.patch_json(encode_item_id + '@@release', {})
    Item.set_status.assert_called_once_with('released')


def test_item_release_endpoint_triggers_set_status(testapp, content, mocker):
    from encoded.types.base import Item
    res = testapp.get('/test-encode-items/')
    encode_item_id = res.json['@graph'][0]['@id']
    mocker.spy(Item, 'set_status')
    testapp.patch_json(encode_item_id + '@@release', {})
    assert Item.set_status.call_count == 1


def test_item_unrelease_endpoint_calls_set_status(testapp, content, mocker):
    from encoded.types.base import Item
    res = testapp.get('/test-encode-items/')
    encode_item_id = res.json['@graph'][0]['@id']
    mocker.patch('encoded.types.base.Item.set_status')
    testapp.patch_json(encode_item_id + '@@unrelease', {})
    Item.set_status.assert_called_once_with('in progress')


@mock_s3
def test_file_release_endpoint_calls_file_set_status(testapp, file, mocker):
    from encoded.types.file import File
    mocker.patch('encoded.types.file.File.set_status')
    testapp.patch_json(file['@id'] + '@@release', {})
    File.set_status.assert_called_once_with('released')


@mock_sts
def test_file_get_external_sheet(testapp, uploading_file, dummy_request, root):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    file_item = root.get_by_uuid(res.json['@graph'][0]['uuid'])
    external = file_item._get_external_sheet()
    assert external['service'] == 's3'
    assert external['bucket'] == 'test_upload_bucket'
    assert 'key' in external


@mock_sts
def test_file_get_external_sheet_not_found(testapp, uploading_file, dummy_request, root):
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    file_item = root.get_by_uuid(res.json['@graph'][0]['uuid'])
    properties = file_item.upgrade_properties()
    # Clear the external sheet.
    file_item.update(properties, sheets={'external': {}})
    with pytest.raises(HTTPNotFound):
        file_item._get_external_sheet()


@mock_sts
@mock_s3
def test_file_release_in_progress_file(testapp, file, dummy_request, root):
    # Create mock bucket.
    import boto3
    client = boto3.client('s3')
    client.create_bucket(Bucket='test_upload_bucket')
    # Generate creds.
    testapp.patch_json(file['@id'], {'status': 'uploading'})
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    testapp.post_json(file['@id'] + '@@upload', {})
    # Get bucket name and key.
    file_item = root.get_by_uuid(file['uuid'])
    external = file_item._get_external_sheet()
    # Pub mock object in bucket.
    client.put_object(Body=b'ABCD', Key=external['key'], Bucket=external['bucket'])
    # Set to in progress.
    testapp.patch_json(file['@id'], {'status': 'in progress'})
    res = testapp.get(file['@id'])
    assert res.json['status'] == 'in progress'
    testapp.patch_json(file['@id'] + '@@release', {})
    res = testapp.get(file['@id'])
    assert res.json['status'] == 'released'


@mock_sts
@mock_s3
def test_file_unrelease_released_file(testapp, file, dummy_request, root):
    # Create mock bucket.
    import boto3
    client = boto3.client('s3')
    client.create_bucket(Bucket='test_upload_bucket')
    # Generate creds.
    testapp.patch_json(file['@id'], {'status': 'uploading'})
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    testapp.post_json(file['@id'] + '@@upload', {})
    # Get bucket name and key.
    file_item = root.get_by_uuid(file['uuid'])
    external = file_item._get_external_sheet()
    # Pub mock object in bucket.
    client.put_object(Body=b'ABCD', Key=external['key'], Bucket=external['bucket'])
    # Manually release.
    testapp.patch_json(file['@id'], {'status': 'released'})
    res = testapp.get(file['@id'])
    assert res.json['status'] == 'released'
    # Go through unrelease trigger.
    testapp.patch_json(file['@id'] + '@@unrelease', {})
    res = testapp.get(file['@id'])
    assert res.json['status'] == 'in progress'


def test_set_public_s3_calls_boto(mocker, testapp, uploading_file, dummy_request, root):
    import boto3
    mocker.patch('boto3.resource')
    # Must have external sheet.
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    file_item = root.get_by_uuid(res.json['@graph'][0]['uuid'])
    file_item.set_public_s3()
    boto3.resource.assert_called_once()


def test_set_private_s3_calls_boto(mocker, testapp, uploading_file, dummy_request, root):
    import boto3
    mocker.patch('boto3.resource')
    # Must have external sheet.
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    file_item = root.get_by_uuid(res.json['@graph'][0]['uuid'])
    file_item.set_private_s3()
    boto3.resource.assert_called_once()
