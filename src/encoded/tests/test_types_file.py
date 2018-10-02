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
def test_public_file_has_google_transfer_metadata(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'google_transfer' in res.json
    gtm = res.json['google_transfer']
    assert 'test_file_bucket' in gtm['url']
    assert 'xyz.bed' in gtm['url']
    assert gtm['md5sum_base64'] == '1B2M2Y8AsgTpgAmY7PhCfg=='
    assert gtm['file_size'] == 34


@pytest.mark.parametrize("file_status", [
    status
    for status in File.private_s3_statuses
    if status != 'replaced'
])
def test_private_file_does_not_have_google_transfer_metadata(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'google_transfer' not in res.json


def test_public_file_with_no_external_sheet_has_blank_google_transfer_metadata(testapp, file):
    testapp.patch_json(file['@id'], {'status': 'released'})
    res = testapp.get(file['@id'])
    assert 'google_transfer' in res.json
    assert not res.json['google_transfer']


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


def test_public_file_no_external_sheet_blank_s3_uri(testapp, file):
    testapp.patch_json(file['@id'], {'status': 'released'})
    res = testapp.get(file['@id'])
    assert 's3_uri' in res.json
    assert not res.json['s3_uri']
