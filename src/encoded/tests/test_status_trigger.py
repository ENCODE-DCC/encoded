import pytest
from moto import (
    mock_s3,
    mock_sts
)
from pyramid.httpexceptions import HTTPNotFound
from datetime import datetime


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


def test_item_set_status_up_down_lists_exists(testapp, content, root):
    res = testapp.get('/test-encode-items/')
    encode_item_uuid = res.json['@graph'][0]['uuid']
    encode_item = root.get_by_uuid(encode_item_uuid)
    assert hasattr(encode_item, 'set_status_up')
    assert hasattr(encode_item, 'set_status_down')
    assert isinstance(encode_item.set_status_up, list)
    assert isinstance(encode_item.set_status_down, list)


def test_item_set_status_no_status_validation_error(testapp, content, root):
    res = testapp.get('/test-encode-items/')
    encode_item_uuid = res.json['@graph'][0]['uuid']
    encode_item_id = res.json['@graph'][0]['@id']
    encode_item = root.get_by_uuid(encode_item_uuid)
    encode_item_properties = encode_item.properties
    encode_item_properties.pop('status')
    encode_item.update(encode_item_properties)
    res = testapp.get(encode_item_id)
    assert 'status' not in res.json
    res = testapp.patch_json(encode_item_id + '@@release', {}, status=422)
    assert res.json['errors'][0]['description'] == 'No property status'


def test_item_set_status_invalid_transition_parent(testapp, content, root, dummy_request):
    # Can't go from deleted to released.
    from snovault.validation import ValidationFailure
    res = testapp.get('/test-encode-items/')
    encode_item_uuid = res.json['@graph'][0]['uuid']
    encode_item_id = res.json['@graph'][0]['@id']
    testapp.patch_json(encode_item_id, {'status': 'deleted'}, status=200)
    encode_item = root.get_by_uuid(encode_item_uuid)
    with pytest.raises(ValidationFailure) as e:
        encode_item.set_status('released', dummy_request)
    assert e.value.detail['description'] == 'Status transition deleted to released not allowed'


def test_item_set_status_invalid_transition_child(testapp, content, root, dummy_request):
    # Don't raise error if invalid transition on child object.
    res = testapp.get('/test-encode-items/')
    encode_item_uuid = res.json['@graph'][0]['uuid']
    encode_item_id = res.json['@graph'][0]['@id']
    testapp.patch_json(encode_item_id, {'status': 'deleted'}, status=200)
    encode_item = root.get_by_uuid(encode_item_uuid)
    assert encode_item.set_status('released', dummy_request, parent=False)[0] is False


def test_item_release_endpoint_calls_set_status(testapp, content, mocker):
    from encoded.types.base import Item
    res = testapp.get('/test-encode-items/')
    encode_item_id = res.json['@graph'][0]['@id']
    mocker.patch('encoded.types.base.Item.set_status')
    testapp.patch_json(encode_item_id + '@@release', {})
    assert Item.set_status.call_count == 1


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
    assert Item.set_status.call_count == 1


@mock_s3
def test_file_release_endpoint_calls_file_set_status(testapp, file, mocker):
    from encoded.types.file import File
    mocker.patch('encoded.types.file.File.set_status')
    testapp.patch_json(file['@id'] + '@@release', {})
    assert File.set_status.call_count == 1


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


@mock_sts
def test_set_public_s3_calls_boto(mocker, testapp, uploading_file, dummy_request, root):
    import boto3
    mocker.patch('boto3.resource')
    # Must have external sheet.
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    file_item = root.get_by_uuid(res.json['@graph'][0]['uuid'])
    file_item.set_public_s3()
    assert boto3.resource.call_count == 1


@mock_sts
def test_set_private_s3_calls_boto(mocker, testapp, uploading_file, dummy_request, root):
    import boto3
    mocker.patch('boto3.resource')
    # Must have external sheet.
    dummy_request.registry.settings['file_upload_bucket'] = 'test_upload_bucket'
    res = testapp.post_json('/file', uploading_file)
    file_item = root.get_by_uuid(res.json['@graph'][0]['uuid'])
    file_item.set_private_s3()
    assert boto3.resource.call_count == 1


def test_set_status_parent_validation_failure(file, root, testapp, dummy_request):
    # Can't go from deleted to released.
    from snovault.validation import ValidationFailure
    testapp.patch_json(file['@id'], {'status': 'deleted'}, status=200)
    file_item = root.get_by_uuid(file['uuid'])
    with pytest.raises(ValidationFailure) as e:
        file_item.set_status('released', dummy_request)
    assert e.value.detail['description'] == 'Status transition deleted to released not allowed'


def test_set_status_child_return(file, root, testapp, dummy_request):
    # Can't go from deleted to released.
    testapp.patch_json(file['@id'], {'status': 'deleted'}, status=200)
    file_item = root.get_by_uuid(file['uuid'])
    res = file_item.set_status('released', dummy_request, parent=False)
    assert not res[0]


def test_set_status_catch_access_denied_error(mocker, testapp, file):
    from botocore.exceptions import ClientError
    from encoded.types.file import File
    from encoded.types.file import logging
    import boto3
    mocker.patch('boto3.resource')
    boto3.resource.side_effect = ClientError(
        {
            'Error': {
                'Code': 'AccessDenied',
                'Message': 'Access Denied'
            }
        },
        'PutObjectAcl'
    )
    mocker.patch('encoded.types.file.File._get_external_sheet')
    File._get_external_sheet.return_value = {}
    mocker.patch('encoded.types.file.logging.warn')
    testapp.patch_json(file['@id'] + '@@release', {})
    # Should log AccessDenied error but shouldn't raise error.
    assert logging.warn.call_count == 2


def test_set_status_raise_other_error(mocker, testapp, file):
    from botocore.exceptions import ClientError
    from encoded.types.file import File
    import boto3
    mocker.patch('boto3.resource')
    boto3.resource.side_effect = ClientError(
        {
            'Error': {
                'Code': 'NoSuchBucket',
                'Message': 'The specified bucket does not exist'
            }
        },
        'ListBucket'
    )
    mocker.patch('encoded.types.file.File._get_external_sheet')
    File._get_external_sheet.return_value = {}
    # Should raise error.
    with pytest.raises(ClientError):
        testapp.patch_json(file['@id'] + '@@release', {})


@mock_sts
@mock_s3
def test_set_status_submitter_denied(testapp, submitter_testapp, file, dummy_request, root):
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
    submitter_testapp.patch_json(file['@id'] + '@@release', {}, status=422)
    res = testapp.get(file['@id'])
    assert res.json['status'] == 'in progress'


@mock_sts
@mock_s3
def test_set_status_in_progress_experiment(testapp, root, experiment, replicate, file, award, lab, dummy_request):
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
    for encode_item in [experiment, file, replicate]:
        res = testapp.get(encode_item['@id'])
        assert res.json['status'] == 'in progress'
    # Release experiment.
    res = testapp.patch_json(experiment['@id'] + '@@release', {})
    # File, exp, and rep now released.
    for encode_item in [experiment, file, replicate]:
        res = testapp.get(encode_item['@id'])
        assert res.json['status'] == 'released'
    # Unrelease experiment.
    res = testapp.patch_json(experiment['@id'] + '@@unrelease', {})
    # File and exp now in progress.
    for encode_item in [experiment, file]:
        res = testapp.get(encode_item['@id'])
        assert res.json['status'] == 'in progress'
    # Replicate remains released.
    res = testapp.get(replicate['@id'])
    assert res.json['status'] == 'released'


def test_set_status_endpoint_status_not_specified(testapp, experiment, dummy_request):
    res = testapp.patch_json(experiment['@id'] + '@@set_status', {}, status=422)
    assert res.json['errors'][0]['description'] == 'Status not specified'


def test_set_status_endpoint_status_specified(testapp, experiment, dummy_request):
    testapp.patch_json(experiment['@id'] + '@@set_status', {'status': 'released'}, status=200)


def test_set_status_endpoint_in_progress_experiment(testapp, experiment, dummy_request):
    res = testapp.get(experiment['@id'])
    assert res.json['status'] == 'in progress'
    testapp.patch_json(experiment['@id'] + '@@set_status', {'status': 'released'})
    res = testapp.get(experiment['@id'])
    assert res.json['status'] == 'released'


def test_set_status_endpoint_released_experiment(testapp, experiment, dummy_request):
    res = testapp.patch_json(experiment['@id'] + '@@set_status', {'status': 'released'})
    res = testapp.get(experiment['@id'])
    assert res.json['status'] == 'released'
    testapp.patch_json(experiment['@id'] + '@@set_status', {'status': 'in progress'})
    res = testapp.get(experiment['@id'])
    assert res.json['status'] == 'in progress'


def test_set_status_endpoint_release_experiment_has_date_released(testapp, experiment, dummy_request):
    res = testapp.get(experiment['@id'])
    assert res.json['status'] == 'in progress'
    assert 'date_released' not in res.json
    testapp.patch_json(experiment['@id'] + '@@set_status', {'status': 'released'})
    res = testapp.get(experiment['@id'])
    assert res.json['status'] == 'released'
    assert 'date_released' in res.json


def test_set_status_endpoint_experiment_date_released_remains_same(testapp, experiment, dummy_request):
    dt = datetime.now().date()
    dt = str(dt.replace(year=dt.year - 10))
    testapp.patch_json(experiment['@id'], {'date_released': dt})
    testapp.patch_json(experiment['@id'] + '@@set_status', {'status': 'released'})
    res = testapp.get(experiment['@id'])
    assert res.json['date_released'] == dt


def test_set_status_invalid_status_validation_failure(file, root, testapp, request):
    from snovault.validation import ValidationFailure
    file_item = root.get_by_uuid(file['uuid'])
    with pytest.raises(ValidationFailure) as e:
        file_item.set_status('submitted', request)
    assert 'submitted not one of' in e.value.detail['description']


def test_set_status_changed_paths_experiment(testapp, experiment, dummy_request):
    res = testapp.patch_json(experiment['@id'] + '@@set_status', {'status': 'released'}, status=200)
    assert len(res.json_body['changed']) == 1


@mock_sts
@mock_s3
def test_set_status_changed_paths_experiment_rep_and_file(testapp, experiment, file, replicate, dummy_request, root):
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
    res = testapp.patch_json(experiment['@id'] + '@@set_status', {'status': 'released'}, status=200)
    assert len(res.json_body['changed']) == 5
    assert len(res.json_body['considered']) == 5


@mock_sts
@mock_s3
def test_set_status_changed_paths_experiment_rep_and_in_progress_file(testapp, experiment, file, replicate, dummy_request, root):
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
    testapp.patch_json(file['@id'], {'status': 'released'})
    res = testapp.patch_json(experiment['@id'] + '@@set_status', {'status': 'released'}, status=200)
    assert len(res.json_body['changed']) == 4
    assert len(res.json_body['considered']) == 5
