import pytest
from encoded.types.file import File
from moto import (
    mock_sts,
    mock_s3
)


@pytest.fixture
def file_with_external_sheet(file, root):
    file_item = root.get_by_uuid(file['uuid'])
    properties = file_item.upgrade_properties()
    file_item.update(
        properties,
        sheets={
            'external': {
                'service': 's3',
                'key': 'xyz.bed',
                'bucket': 'test_file_bucket',
            }
        }
    )
    return file


@mock_sts
@mock_s3
@pytest.mark.parametrize("file_status", [
    status
    for status in File.public_s3_statuses
])
def test_public_file_has_cloud_metadata(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'cloud_metadata' in res.json
    cm = res.json['cloud_metadata']
    assert 'test_file_bucket' in cm['url']
    assert 'xyz.bed' in cm['url']
    assert cm['md5sum_base64'] == '1B2M2Y8AsgTpgAmY7PhCfg=='
    assert cm['file_size'] == 34


def test_public_restricted_file_does_not_have_cloud_metadata(testapp, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'restricted': True
        }
    )
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'cloud_metadata' not in res.json


@pytest.mark.parametrize("file_status", [
    status
    for status in File.private_s3_statuses
    if status != 'replaced'
])
def test_private_file_does_not_have_cloud_metadata(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'cloud_metadata' not in res.json


def test_public_file_with_no_external_sheet_no_cloud_metadata(testapp, file):
    testapp.patch_json(file['@id'], {'status': 'released'})
    res = testapp.get(file['@id'])
    assert 'cloud_metadata' not in res.json


@pytest.mark.parametrize("file_status", [
    status
    for status in File.public_s3_statuses
])
def test_public_file_has_s3_uri(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 's3_uri' in res.json
    assert res.json['s3_uri'] == 's3://test_file_bucket/xyz.bed'


@pytest.mark.parametrize("file_status", [
    status
    for status in File.private_s3_statuses
    if status != 'replaced'
])
def test_private_file_does_not_have_s3_uri(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 's3_uri' not in res.json


def test_public_file_no_external_sheet_no_s3_uri(testapp, file):
    testapp.patch_json(file['@id'], {'status': 'released'})
    res = testapp.get(file['@id'])
    assert 's3_uri' not in res.json


def test_public_restricted_file_does_not_have_s3_uri(testapp, file_with_external_sheet):
    testapp.patch_json(
        file_with_external_sheet['@id'],
        {
            'status': 'released',
            'restricted': True,
        }
    )
    res = testapp.get(file_with_external_sheet['@id'])
    assert 's3_uri' not in res.json
