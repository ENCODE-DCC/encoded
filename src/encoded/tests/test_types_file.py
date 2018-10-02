import pytest
from encoded.types.file import File


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
                'bucket': 'test_upload_bucket',
            }
        }
    )
    return file


@pytest.mark.parametrize("file_status", [
    status
    for status in File.public_s3_statuses
])
def test_public_file_has_google_transfer_metadata(testapp, file_with_external_sheet, file_status):
    testapp.patch_json(file_with_external_sheet['@id'], {'status': file_status})
    res = testapp.get(file_with_external_sheet['@id'])
    assert 'google_transfer' in res.json
    gtm = res.json['google_transfer']
    assert gtm['url'] == 'https://encode-files.s3.amazonaws.com/xyz.bed'
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
